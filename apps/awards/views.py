from django.shortcuts import render
from .models import AwardCategory, NominationPeriod

def landing_view(request):
    period = NominationPeriod.get_current()
    categories = AwardCategory.objects.filter(is_active=True).order_by('display_order', 'id')
    context = {
        'period': period,
        'categories': categories,
        'categories_count': categories.count(),
    }
    return render(request, 'pages/landing.html', context)

