import json
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.awards.models import AwardCategory, NominationPeriod
from .models import NominationDraft, DraftEntry, Nomination
from .services import (
    check_nomination_eligibility,
    get_or_create_user_draft,
    submit_nomination_draft,
    user_has_verified_email,
)

@login_required
def wizard_view(request):
    period = NominationPeriod.get_current()
    if period.maintenance_mode:
        return render(request, 'nominations/maintenance.html', {'period': period})
    if not period.is_open:
        messages.warning(request, "Nominations are currently closed.")
        return redirect('landing')

    if settings.REQUIRE_EMAIL_VERIFICATION and not user_has_verified_email(request.user):
        return render(request, 'accounts/email_verification_sent.html', {
            'email': request.user.email,
            'message': 'Please verify your email address to access the nomination portal.'
        })

    draft = get_or_create_user_draft(request.user)
    if draft.status == 'submitted':
        return redirect('nominations:success')

    categories = AwardCategory.objects.filter(is_active=True).order_by('display_order', 'id')
    # Build a lookup of existing draft entries
    entries_by_cat = {entry.category_id: entry for entry in draft.entries.all()}

    steps_data = []
    for index, cat in enumerate(categories, start=1):
        entry = entries_by_cat.get(cat.id)
        steps_data.append({
            'step_number': index,
            'category': cat,
            'entry': entry,
        })

    context = {
        'draft': draft,
        'steps_data': steps_data,
        'total_steps': len(steps_data),
    }
    return render(request, 'nominations/wizard.html', context)


@login_required
@require_POST
def save_draft_entry_view(request):
    draft = get_or_create_user_draft(request.user)
    if draft.status == 'submitted':
        return JsonResponse({'status': 'error', 'message': 'Nominations already submitted.'}, status=400)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST

        category_id = data.get('category_id')
        if not category_id:
            return JsonResponse({'status': 'error', 'message': 'Category ID is required.'}, status=400)

        category = get_object_or_404(AwardCategory, pk=category_id, is_active=True)
        entry, _ = DraftEntry.objects.get_or_create(draft=draft, category=category)

        entry.skipped = str(data.get('skipped', 'false')).lower() in ('true', '1', 'yes')
        entry.nom_a_first = data.get('nom_a_first', '').strip()
        entry.nom_a_last = data.get('nom_a_last', '').strip()
        entry.nom_a_programme = data.get('nom_a_programme', '').strip()

        entry.nom_b_first = data.get('nom_b_first', '').strip()
        entry.nom_b_last = data.get('nom_b_last', '').strip()
        entry.nom_b_programme = data.get('nom_b_programme', '').strip()

        entry.save()
        return JsonResponse({'status': 'success', 'category_id': category.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def review_view(request):
    if settings.REQUIRE_EMAIL_VERIFICATION and not user_has_verified_email(request.user):
        messages.error(request, "Please verify your email address before reviewing your nominations.")
        return redirect('nominate_wizard')

    draft = get_or_create_user_draft(request.user)
    if draft.status == 'submitted':
        return redirect('nominations:success')

    categories = AwardCategory.objects.filter(is_active=True).order_by('display_order', 'id')
    entries_by_cat = {entry.category_id: entry for entry in draft.entries.all()}

    review_list = []
    filled_count = 0
    skipped_count = 0

    for idx, cat in enumerate(categories, start=1):
        entry = entries_by_cat.get(cat.id)
        is_filled = False
        if entry and not entry.skipped and (entry.nom_a_first or entry.nom_a_last):
            is_filled = True
            filled_count += 1
        elif entry and entry.skipped:
            skipped_count += 1

        review_list.append({
            'step_number': idx,
            'category': cat,
            'entry': entry,
            'is_filled': is_filled,
        })

    context = {
        'draft': draft,
        'review_list': review_list,
        'filled_count': filled_count,
        'skipped_count': skipped_count,
        'total_count': len(review_list),
    }
    return render(request, 'nominations/review.html', context)


@login_required
@require_POST
def submit_view(request):
    try:
        nominations = submit_nomination_draft(request.user)
        messages.success(request, f"Congratulations! Your nominations ({len(nominations)} categories) have been officially submitted!")
        return redirect('nominations:success')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('nominations:review')


@login_required
def success_view(request):
    nominations = Nomination.objects.filter(nominator=request.user).select_related('category').order_by('category__display_order')
    return render(request, 'nominations/success.html', {
        'nominations': nominations,
        'nomination_count': nominations.count()
    })

