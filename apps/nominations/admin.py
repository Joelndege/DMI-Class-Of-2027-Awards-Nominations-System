from django.contrib import admin
from .models import (
    NominationDraft,
    DraftEntry,
    Nomination,
    NameVariantGroup,
    NameVariant,
    Finalist,
    Winner,
    AuditEvent,
)

@admin.register(NominationDraft)
class NominationDraftAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'submitted_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'user__username')

@admin.register(DraftEntry)
class DraftEntryAdmin(admin.ModelAdmin):
    list_display = ('draft', 'category', 'nom_a_first', 'nom_a_last', 'skipped', 'updated_at')
    list_filter = ('skipped', 'category')
    search_fields = ('nom_a_first', 'nom_a_last', 'draft__user__email')

@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ('category', 'nominator', 'nom_a_first', 'nom_a_last', 'nom_b_first', 'nom_b_last', 'submitted_at')
    list_filter = ('category', 'submitted_at')
    search_fields = ('nom_a_first', 'nom_a_last', 'nom_b_first', 'nom_b_last', 'nominator__email')

class NameVariantInline(admin.TabularInline):
    model = NameVariant
    extra = 1

@admin.register(NameVariantGroup)
class NameVariantGroupAdmin(admin.ModelAdmin):
    list_display = ('canonical_name', 'category', 'status', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('canonical_name',)
    inlines = [NameVariantInline]

@admin.register(Finalist)
class FinalistAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slot_label', 'selected_at', 'selected_by')
    list_filter = ('category', 'slot_label')
    search_fields = ('name',)

@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slot_label', 'announced_at', 'selected_by')
    list_filter = ('category', 'slot_label')
    search_fields = ('name',)

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor', 'created_at')
    list_filter = ('action',)
    search_fields = ('details', 'actor__email')
    readonly_fields = ('created_at',)

