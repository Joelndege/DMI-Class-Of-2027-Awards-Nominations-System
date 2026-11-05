from django.test import TestCase
from django.urls import reverse
from apps.awards.models import AwardCategory, NominationPeriod

class AwardsModelTestCase(TestCase):
    def setUp(self):
        self.category = AwardCategory.objects.create(
            name='Best Innovator',
            slot_type='single',
            slot_a_label='Nominee',
            display_order=1
        )

    def test_slug_auto_generation(self):
        self.assertEqual(self.category.slug, 'best-innovator')

    def test_nomination_period_singleton(self):
        p1 = NominationPeriod.get_current()
        p2 = NominationPeriod.get_current()
        self.assertEqual(p1.pk, 1)
        self.assertEqual(p1.pk, p2.pk)
        self.assertTrue(p1.is_open)
        self.assertFalse(p1.maintenance_mode)

    def test_landing_page_view(self):
        url = reverse('landing')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Best Innovator')
        self.assertTemplateUsed(response, 'pages/landing.html')

