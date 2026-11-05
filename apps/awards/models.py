from django.db import models
from django.utils.text import slugify
from django.utils import timezone

class AwardCategory(models.Model):
    SLOT_TYPE_CHOICES = (
        ('single', 'Single'),
        ('gendered', 'Male+Female / Mami+Papi'),
        ('pair', 'Pair'),
    )

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, default='')
    slot_type = models.CharField(max_length=20, choices=SLOT_TYPE_CHOICES, default='single')
    slot_a_label = models.CharField(max_length=100, default='Nominee')
    slot_b_label = models.CharField(max_length=100, blank=True, default='')
    accepts_online_nominations = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Award Category'
        verbose_name_plural = 'Award Categories'

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while AwardCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class NominationPeriod(models.Model):
    is_open = models.BooleanField(default=True)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    maintenance_mode = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Nomination Period'
        verbose_name_plural = 'Nomination Period'

    @classmethod
    def get_current(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Nomination Period (Open: {self.is_open}, Maintenance: {self.maintenance_mode})"
