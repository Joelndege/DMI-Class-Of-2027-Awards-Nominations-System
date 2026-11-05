from django.contrib import admin
from .models import AwardCategory, NominationPeriod

@admin.register(AwardCategory)
class AwardCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slot_type', 'display_order', 'accepts_online_nominations', 'is_active')
    list_editable = ('display_order', 'accepts_online_nominations', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(NominationPeriod)
class NominationPeriodAdmin(admin.ModelAdmin):
    list_display = ('is_open', 'start_at', 'end_at', 'maintenance_mode')

