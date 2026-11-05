from django.db import models
from django.conf import settings

class NominationDraft(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nomination_draft'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Draft by {self.user} ({self.status})"


class DraftEntry(models.Model):
    draft = models.ForeignKey(
        NominationDraft,
        on_delete=models.CASCADE,
        related_name='entries'
    )
    category = models.ForeignKey(
        'awards.AwardCategory',
        on_delete=models.PROTECT,
        related_name='draft_entries'
    )
    # Slot A
    nom_a_first = models.CharField(max_length=100, blank=True, default='')
    nom_a_last = models.CharField(max_length=100, blank=True, default='')
    nom_a_programme = models.CharField(max_length=150, blank=True, default='')

    # Slot B (for gendered/pair)
    nom_b_first = models.CharField(max_length=100, blank=True, default='')
    nom_b_last = models.CharField(max_length=100, blank=True, default='')
    nom_b_programme = models.CharField(max_length=150, blank=True, default='')

    skipped = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['draft', 'category'], name='unique_draft_category')
        ]
        verbose_name = 'Draft Entry'
        verbose_name_plural = 'Draft Entries'

    def __str__(self):
        return f"{self.draft.user.email} - {self.category.name} ({'Skipped' if self.skipped else 'Filled'})"


class Nomination(models.Model):
    draft = models.ForeignKey(
        NominationDraft,
        on_delete=models.PROTECT,
        related_name='nominations'
    )
    category = models.ForeignKey(
        'awards.AwardCategory',
        on_delete=models.PROTECT,
        related_name='nominations'
    )
    nominator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='submitted_nominations'
    )

    # Slot A
    nom_a_first = models.CharField(max_length=100)
    nom_a_last = models.CharField(max_length=100)
    nom_a_programme = models.CharField(max_length=150, blank=True, default='')

    # Slot B
    nom_b_first = models.CharField(max_length=100, blank=True, default='')
    nom_b_last = models.CharField(max_length=100, blank=True, default='')
    nom_b_programme = models.CharField(max_length=150, blank=True, default='')

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nominator', 'category'], name='unique_nominator_category')
        ]
        ordering = ['-submitted_at']
        verbose_name = 'Nomination'
        verbose_name_plural = 'Nominations'

    def __str__(self):
        slot_a = f"{self.nom_a_first} {self.nom_a_last}".strip()
        if self.nom_b_first or self.nom_b_last:
            slot_b = f"{self.nom_b_first} {self.nom_b_last}".strip()
            return f"{self.category.name}: {slot_a} & {slot_b} (by {self.nominator})"
        return f"{self.category.name}: {slot_a} (by {self.nominator})"


class NameVariantGroup(models.Model):
    STATUS_CHOICES = (
        ('review', 'Under Review'),
        ('same', 'Same Person'),
        ('different', 'Different People'),
    )

    category = models.ForeignKey(
        'awards.AwardCategory',
        on_delete=models.CASCADE,
        related_name='name_groups'
    )
    canonical_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='review')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.canonical_name} ({self.get_status_display()}) - {self.category.name}"


class NameVariant(models.Model):
    group = models.ForeignKey(
        NameVariantGroup,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    submitted_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.submitted_name} -> {self.group.canonical_name}"


class Finalist(models.Model):
    category = models.ForeignKey(
        'awards.AwardCategory',
        on_delete=models.CASCADE,
        related_name='finalists'
    )
    slot_label = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True, default='')
    selected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    selected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Finalist: {self.name} - {self.category.name} ({self.slot_label})"


class Winner(models.Model):
    category = models.ForeignKey(
        'awards.AwardCategory',
        on_delete=models.CASCADE,
        related_name='winners'
    )
    slot_label = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    notes = models.TextField(blank=True, default='')
    selected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    selected_at = models.DateTimeField(auto_now_add=True)
    announced_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Winner: {self.name} - {self.category.name} ({self.slot_label})"


class AuditEvent(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} by {self.actor or 'System'} at {self.created_at}"

