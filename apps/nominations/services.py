from django.conf import settings
from django.db import transaction
from django.utils import timezone
from apps.awards.models import AwardCategory, NominationPeriod
from .models import NominationDraft, DraftEntry, Nomination, AuditEvent
from allauth.account.models import EmailAddress

def user_has_verified_email(user):
    if not user.is_authenticated:
        return False
    # Check profile flag
    if hasattr(user, 'profile') and user.profile.email_verified:
        return True
    # Check allauth EmailAddress records
    if EmailAddress.objects.filter(user=user, verified=True).exists():
        if hasattr(user, 'profile'):
            user.profile.email_verified = True
            user.profile.save()
        return True
    # If superuser or staff during tests/dev
    if user.is_staff or user.is_superuser:
        return True
    return False

def check_nomination_eligibility(user):
    period = NominationPeriod.get_current()
    if period.maintenance_mode:
        return False, "The nomination portal is currently undergoing scheduled maintenance. Please check back soon."
    if not period.is_open:
        return False, "Nominations are currently closed."
    if settings.REQUIRE_EMAIL_VERIFICATION and not user_has_verified_email(user):
        return False, "Your email address must be verified before submitting nominations."
    return True, ""

def get_or_create_user_draft(user):
    draft, _ = NominationDraft.objects.get_or_create(user=user)
    # Ensure draft entries exist for all active award categories
    categories = AwardCategory.objects.filter(is_active=True).order_by('display_order', 'id')
    for cat in categories:
        DraftEntry.objects.get_or_create(draft=draft, category=cat)
    return draft

def submit_nomination_draft(user):
    with transaction.atomic():
        can_nominate, reason = check_nomination_eligibility(user)
        if not can_nominate:
            raise ValueError(reason)

        draft = NominationDraft.objects.select_for_update().get(user=user)
        if draft.status == 'submitted':
            raise ValueError("You have already submitted your nominations.")

        created_nominations = []
        entries = draft.entries.select_related('category').filter(category__is_active=True)

        for entry in entries:
            # If category does not accept online nominations or entry is marked skipped
            if not entry.category.accepts_online_nominations or entry.skipped:
                continue

            first_a = entry.nom_a_first.strip()
            last_a = entry.nom_a_last.strip()

            # For single slot: requires at least first_a
            if not first_a:
                continue

            nomination, _ = Nomination.objects.update_or_create(
                nominator=user,
                category=entry.category,
                defaults={
                    'draft': draft,
                    'nom_a_first': first_a,
                    'nom_a_last': last_a,
                    'nom_a_programme': entry.nom_a_programme.strip(),
                    'nom_b_first': entry.nom_b_first.strip(),
                    'nom_b_last': entry.nom_b_last.strip(),
                    'nom_b_programme': entry.nom_b_programme.strip(),
                }
            )
            created_nominations.append(nomination)

        draft.status = 'submitted'
        draft.submitted_at = timezone.now()
        draft.save()

        AuditEvent.objects.create(
            actor=user,
            action='NOMINATIONS_SUBMITTED',
            details=f"User {user.email} submitted {len(created_nominations)} nominations."
        )

        return created_nominations

