from .base import *
import os

DEBUG = False

# Railway injects RAILWAY_PUBLIC_DOMAIN after a public domain has been created.
# ALLOWED_HOSTS can also be set explicitly for Railway or a custom domain.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', os.getenv('RAILWAY_PUBLIC_DOMAIN', '')).split(',')
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise RuntimeError('Set ALLOWED_HOSTS or create a Railway public domain before deploying.')

# Django requires origins (including scheme) for POST requests behind HTTPS.
_railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip()
_default_csrf_origins = f'https://{_railway_domain}' if _railway_domain else ''
CSRF_TRUSTED_ORIGINS = [
    origin.strip().rstrip('/')
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', _default_csrf_origins).split(',')
    if origin.strip()
]

if not os.getenv('SECRET_KEY') or SECRET_KEY.startswith('django-insecure-'):
    raise RuntimeError('Set SECRET_KEY to a unique, randomly generated value in Railway.')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Email stays in the console backend unless SMTP is configured. Set these in
# Railway if the app should send verification, reset, or notification emails.
EMAIL_HOST = os.getenv('EMAIL_HOST', '').strip()
if EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('true', '1', 't')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', DEFAULT_FROM_EMAIL)

