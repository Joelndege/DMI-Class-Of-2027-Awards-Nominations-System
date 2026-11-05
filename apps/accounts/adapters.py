from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from allauth.account.models import EmailAddress

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True

    def get_login_redirect_url(self, request):
        return '/nominate/'

    def confirm_email(self, request, email_address):
        super().confirm_email(request, email_address)
        user = email_address.user
        if hasattr(user, 'profile'):
            user.profile.email_verified = True
            user.profile.save()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def on_authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        import sys, traceback
        print("\n" + "="*50, file=sys.stderr)
        print(f"OAUTH AUTHENTICATION ERROR DETECTED:", file=sys.stderr)
        print(f"Provider: {provider}", file=sys.stderr)
        print(f"Error Code: {error}", file=sys.stderr)
        print(f"Exception: {type(exception).__name__}: {exception}", file=sys.stderr)
        print(f"Extra Context: {extra_context}", file=sys.stderr)
        if exception:
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
        print("="*50 + "\n", file=sys.stderr)
        super().on_authentication_error(request, provider, error=error, exception=exception, extra_context=extra_context)

    def pre_social_login(self, request, sociallogin):
        # Prevent auto-linking unverified social account emails
        email = sociallogin.user.email
        if not email:
            return

        social_verified = False
        if sociallogin.account.extra_data:
            social_verified = bool(sociallogin.account.extra_data.get('email_verified', False))

        try:
            email_address = EmailAddress.objects.get(email__iexact=email)
            if not social_verified:
                messages.error(request, "Cannot link an unverified external email address.")
                raise ImmediateHttpResponse(redirect('/accounts/login/'))
            if not sociallogin.is_existing:
                sociallogin.connect(request, email_address.user)
        except EmailAddress.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        social_verified = False
        picture = ''
        if sociallogin.account.extra_data:
            social_verified = bool(sociallogin.account.extra_data.get('email_verified', False))
            picture = sociallogin.account.extra_data.get('picture', '')

        if hasattr(user, 'profile'):
            if social_verified:
                user.profile.email_verified = True
            if picture and not user.profile.avatar_url:
                user.profile.avatar_url = picture
            user.profile.save()
        return user
