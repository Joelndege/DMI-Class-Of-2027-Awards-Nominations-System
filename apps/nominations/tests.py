import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.awards.models import AwardCategory, NominationPeriod
from apps.nominations.models import (
    NominationDraft,
    DraftEntry,
    Nomination,
    AuditEvent,
)
from apps.nominations.services import (
    get_or_create_user_draft,
    submit_nomination_draft,
)

User = get_user_model()

class NominationsTestCase(TestCase):
    def setUp(self):
        self.period = NominationPeriod.get_current()
        self.period.is_open = True
        self.period.maintenance_mode = False
        self.period.save()

        self.cat1 = AwardCategory.objects.create(
            name='Yaza of the Batch',
            slot_type='gendered',
            slot_a_label='Male Yaza',
            slot_b_label='Female Yaza',
            display_order=1
        )
        self.cat2 = AwardCategory.objects.create(
            name='Swazi of the Batch',
            slot_type='single',
            slot_a_label='Nominee',
            display_order=2
        )

        self.user = User.objects.create_user(
            username='student@dmi2027.edu',
            email='student@dmi2027.edu',
            password='TestPassword123!'
        )
        self.user.profile.email_verified = True
        self.user.profile.save()

    def test_login_session_allows_wizard_and_review_then_logout(self):
        response = self.client.post(reverse('account_login'), {
            'login': self.user.email,
            'password': 'TestPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

        self.assertEqual(self.client.get(reverse('nominations:wizard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('nominations:review')).status_code, 200)

        self.client.post(reverse('account_logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.get(reverse('nominations:wizard')).status_code, 302)

    def test_draft_and_entries_creation(self):
        draft = get_or_create_user_draft(self.user)
        self.assertEqual(draft.user, self.user)
        self.assertEqual(draft.status, 'draft')
        self.assertEqual(draft.entries.count(), 2)

    def test_save_draft_entry_endpoint(self):
        self.client.force_login(self.user)
        payload = {
            'category_id': self.cat1.id,
            'nom_a_first': 'Alex',
            'nom_a_last': 'Mwale',
            'nom_a_programme': 'Computer Science',
            'nom_b_first': 'Sarah',
            'nom_b_last': 'Phiri',
            'nom_b_programme': 'Law',
            'skipped': False,
        }
        url = reverse('nominations:save_draft')
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')

        draft = NominationDraft.objects.get(user=self.user)
        entry = draft.entries.get(category=self.cat1)
        self.assertEqual(entry.nom_a_first, 'Alex')
        self.assertEqual(entry.nom_b_first, 'Sarah')
        self.assertFalse(entry.skipped)

    def test_submission_service_creates_nominations_and_audit(self):
        draft = get_or_create_user_draft(self.user)
        e1 = draft.entries.get(category=self.cat1)
        e1.nom_a_first = 'Alex'
        e1.nom_a_last = 'Mwale'
        e1.nom_b_first = 'Sarah'
        e1.nom_b_last = 'Phiri'
        e1.save()

        e2 = draft.entries.get(category=self.cat2)
        e2.skipped = True
        e2.save()

        created_noms = submit_nomination_draft(self.user)
        self.assertEqual(len(created_noms), 1)

        nom = Nomination.objects.get(nominator=self.user, category=self.cat1)
        self.assertEqual(nom.nom_a_first, 'Alex')
        self.assertEqual(nom.nom_b_first, 'Sarah')

        draft.refresh_from_db()
        self.assertEqual(draft.status, 'submitted')
        self.assertIsNotNone(draft.submitted_at)

        # Audit event verified
        audit = AuditEvent.objects.filter(actor=self.user, action='NOMINATIONS_SUBMITTED')
        self.assertTrue(audit.exists())

    def test_prevent_double_submission(self):
        draft = get_or_create_user_draft(self.user)
        e1 = draft.entries.get(category=self.cat1)
        e1.nom_a_first = 'Alex'
        e1.nom_a_last = 'Mwale'
        e1.save()

        submit_nomination_draft(self.user)

        with self.assertRaises(ValueError):
            submit_nomination_draft(self.user)

    def test_unverified_user_can_access_wizard_for_testing(self):
        unverified_user = User.objects.create_user(
            username='unverified@dmi2027.edu',
            email='unverified@dmi2027.edu',
            password='Password123!'
        )
        self.client.force_login(unverified_user)
        url = reverse('nominations:wizard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Check Your Inbox')

