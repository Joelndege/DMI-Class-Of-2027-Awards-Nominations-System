from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'programme', 'email_verified', 'created_at')
    search_fields = ('user__email', 'user__username', 'programme')
    list_filter = ('email_verified',)

