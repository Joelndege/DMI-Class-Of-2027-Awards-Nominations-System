from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import UserProfile
from apps.nominations.services import user_has_verified_email

User = get_user_model()

class AccountsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student@dmi2027.edu',
            email='student@dmi2027.edu',
            password='TestPassword123!'
        )

    def test_user_profile_auto_created(self):
        """Profile should be automatically created via post_save signal."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
        self.assertFalse(self.user.profile.email_verified)

    def test_profile_update(self):
        """Updating programme should save correctly."""
        self.user.profile.programme = 'Computer Science'
        self.user.profile.save()
        self.assertEqual(UserProfile.objects.get(user=self.user).programme, 'Computer Science')

    def test_verified_email_helper(self):
        """Unverified user returns False, verified user returns True."""
        self.assertFalse(user_has_verified_email(self.user))
        self.user.profile.email_verified = True
        self.user.profile.save()
        self.assertTrue(user_has_verified_email(self.user))

    def test_staff_user_is_eligible(self):
        """Staff users are considered eligible."""
        staff = User.objects.create_user(
            username='staff@dmi2027.edu',
            email='staff@dmi2027.edu',
            password='Password123!',
            is_staff=True
        )
        self.assertTrue(user_has_verified_email(staff))

    def test_login_with_email_and_username_and_reject_bad_password(self):
        for identifier in (self.user.email, self.user.username):
            response = self.client.post('/accounts/login/', {
                'login': identifier,
                'password': 'TestPassword123!',
            })
            self.assertRedirects(response, '/nominate/', fetch_redirect_response=False)
            self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
            self.client.post('/accounts/logout/')

        response = self.client.post('/accounts/login/', {
            'login': self.user.email,
            'password': 'incorrect-password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_google_provider_is_not_active(self):
        from django.conf import settings
        self.assertNotIn('allauth.socialaccount.providers.google', settings.INSTALLED_APPS)
        self.assertEqual(settings.ACCOUNT_EMAIL_VERIFICATION, 'none')
        login_page = self.client.get('/accounts/login/')
        signup_page = self.client.get('/accounts/signup/')
        self.assertNotContains(login_page, 'Continue with Google')
        self.assertNotContains(signup_page, 'Register with Google')
