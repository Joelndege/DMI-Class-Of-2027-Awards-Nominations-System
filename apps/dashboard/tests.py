from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.awards.models import AwardCategory, NominationPeriod
from apps.nominations.models import Nomination, NominationDraft, NameVariantGroup

User = get_user_model()

class DashboardTestCase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='admin@dmi2027.edu',
            email='admin@dmi2027.edu',
            password='AdminPassword123!',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='student@dmi2027.edu',
            email='student@dmi2027.edu',
            password='StudentPassword123!'
        )
        self.category = AwardCategory.objects.create(
            name='Resilient of the Batch',
            slot_type='single',
            display_order=1
        )

    def test_regular_user_cannot_access_dashboard(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('dashboard:overview'))
        # Should redirect to login or admin login
        self.assertEqual(response.status_code, 302)

    def test_staff_user_accesses_overview(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/overview.html')

    def test_staff_toggles_period(self):
        self.client.force_login(self.staff_user)
        period = NominationPeriod.get_current()
        initial_open = period.is_open

        response = self.client.post(reverse('dashboard:toggle_period'), {
            'action': 'toggle_open'
        })
        self.assertEqual(response.status_code, 302)

        period.refresh_from_db()
        self.assertNotEqual(period.is_open, initial_open)

    def test_nominations_csv_export(self):
        self.client.force_login(self.staff_user)
        draft = NominationDraft.objects.create(user=self.regular_user, status='submitted')
        Nomination.objects.create(
            draft=draft,
            category=self.category,
            nominator=self.regular_user,
            nom_a_first='Grace',
            nom_a_last='Banda'
        )

        url = f"{reverse('dashboard:nominations')}?export=csv"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="nominations_export.csv"', response['Content-Disposition'])
        self.assertContains(response, 'Grace')
        self.assertContains(response, 'Banda')

    def test_create_name_variant_group(self):
        self.client.force_login(self.staff_user)
        url = reverse('dashboard:name_review')
        response = self.client.post(url, {
            'action': 'create_group',
            'canonical_name': 'Grace Banda',
            'selected_names': ['Grace Banda', 'G. Banda'],
            'category': self.category.id
        })
        self.assertEqual(response.status_code, 302)
        group = NameVariantGroup.objects.filter(canonical_name='Grace Banda', category=self.category)
        self.assertTrue(group.exists())

