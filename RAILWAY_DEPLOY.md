# Railway deployment variables

The repository includes `railway.json` with the static-file build, database migrations, and Gunicorn start command. Railway provides `PORT`; do not set it yourself.

## Required service variables

Add these under your Django service's **Variables** tab:

| Variable | Value |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | A unique random secret; generate one with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` and keep it private. |
| `DATABASE_URL` | Reference the PostgreSQL service, for example `${{Postgres.DATABASE_URL}}` if the service is named `Postgres`. |

Create a Railway PostgreSQL service and reference its `DATABASE_URL` in the Django service. Without it, Django falls back to SQLite, whose data is not persistent across Railway deployments.

## Domain and CSRF

After creating a public domain for the Django service, set:

| Variable | Value |
| --- | --- |
| `ALLOWED_HOSTS` | `${{RAILWAY_PUBLIC_DOMAIN}}` (or your exact host name, without `https://`) |
| `CSRF_TRUSTED_ORIGINS` | `https://${{RAILWAY_PUBLIC_DOMAIN}}` (or the full `https://` origin for your custom domain) |

The production settings can infer these from `RAILWAY_PUBLIC_DOMAIN`; set them explicitly if you use a custom domain. For multiple hosts or origins, separate values with commas.

## Optional email delivery

The app uses Django's console email backend unless SMTP is configured. Add these to Railway if you want account and notification emails delivered:

| Variable | Typical value |
| --- | --- |
| `EMAIL_HOST` | Your email provider's SMTP host |
| `EMAIL_PORT` | `587` for TLS, or your provider's port |
| `EMAIL_HOST_USER` | SMTP username |
| `EMAIL_HOST_PASSWORD` | SMTP password or provider app password; treat as a secret |
| `EMAIL_USE_TLS` | `True` for STARTTLS, commonly on port 587 |
| `EMAIL_USE_SSL` | `False` for STARTTLS; use `True` only if your provider requires implicit TLS |
| `DEFAULT_FROM_EMAIL` | A sender address verified with your email provider |

Use the exact host, port, TLS mode, and sender requirements from your email provider. Do not enable TLS and SSL together.

## Google sign-in

`GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are optional settings, but Google sign-in is currently disabled: the Google provider is not installed in `INSTALLED_APPS`. Adding these variables alone will not create a Google button or enable OAuth. OAuth also requires the Google client credentials and an authorized callback URL for the deployed domain.

Do not commit real credentials or secret values to the repository. Use Railway's Variables tab for production secrets.
