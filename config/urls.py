from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.awards.views import landing_view
from apps.nominations.views import wizard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('nominate/', include('apps.nominations.urls')),
    path('nominate-wizard/', wizard_view, name='nominate_wizard'),
    path('dashboard/', include('apps.dashboard.urls')),
    path('awards/', include('apps.awards.urls')),
    path('', landing_view, name='landing'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
