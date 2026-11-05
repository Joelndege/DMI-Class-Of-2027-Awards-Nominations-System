from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from apps.awards.models import AwardCategory, NominationPeriod
from apps.nominations.models import (
    Nomination,
    NominationDraft,
    NameVariantGroup,
    NameVariant,
    AuditEvent,
    Finalist,
    Winner,
)
from .filters import filter_nominations
from .exporters import export_nominations_to_csv

@staff_member_required
def overview_view(request):
    period = NominationPeriod.get_current()
    total_nominations = Nomination.objects.count()
    total_nominators = NominationDraft.objects.filter(status='submitted').count()
    active_categories = AwardCategory.objects.filter(is_active=True).count()
    dinner_categories = AwardCategory.objects.filter(accepts_online_nominations=False).count()

    recent_nominations = Nomination.objects.select_related('category', 'nominator').order_by('-submitted_at')[:8]
    audit_events = AuditEvent.objects.select_related('actor').order_by('-created_at')[:8]

    # Top nominated categories
    top_categories = AwardCategory.objects.annotate(
        nom_count=Count('nominations')
    ).order_by('-nom_count')[:5]

    context = {
        'period': period,
        'total_nominations': total_nominations,
        'total_nominators': total_nominators,
        'active_categories': active_categories,
        'dinner_categories': dinner_categories,
        'recent_nominations': recent_nominations,
        'audit_events': audit_events,
        'top_categories': top_categories,
    }
    return render(request, 'dashboard/overview.html', context)


@staff_member_required
def toggle_period_view(request):
    if request.method == 'POST':
        period = NominationPeriod.get_current()
        action = request.POST.get('action')
        if action == 'toggle_open':
            period.is_open = not period.is_open
            AuditEvent.objects.create(
                actor=request.user,
                action='PERIOD_TOGGLED',
                details=f"Nomination period set to {'OPEN' if period.is_open else 'CLOSED'}."
            )
            messages.success(request, f"Nomination period status set to: {'OPEN' if period.is_open else 'CLOSED'}")
        elif action == 'toggle_maintenance':
            period.maintenance_mode = not period.maintenance_mode
            AuditEvent.objects.create(
                actor=request.user,
                action='MAINTENANCE_TOGGLED',
                details=f"Maintenance mode set to {'ENABLED' if period.maintenance_mode else 'DISABLED'}."
            )
            messages.success(request, f"Maintenance mode set to: {'ENABLED' if period.maintenance_mode else 'DISABLED'}")
        period.save()
    return redirect('dashboard:overview')


@staff_member_required
def categories_view(request):
    categories = AwardCategory.objects.annotate(
        nom_count=Count('nominations')
    ).order_by('display_order', 'id')

    if request.method == 'POST':
        action = request.POST.get('action')
        cat_id = request.POST.get('category_id')
        cat = get_object_or_404(AwardCategory, pk=cat_id)

        if action == 'toggle_active':
            cat.is_active = not cat.is_active
            cat.save()
            messages.success(request, f"Updated {cat.name} active state.")
        elif action == 'toggle_online':
            cat.accepts_online_nominations = not cat.accepts_online_nominations
            cat.save()
            messages.success(request, f"Updated {cat.name} online nominations mode.")
        return redirect('dashboard:categories')

    context = {
        'categories': categories,
    }
    return render(request, 'dashboard/categories.html', context)


@staff_member_required
def nominations_view(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('q', '').strip()
    programme = request.GET.get('programme', '').strip()

    qs = Nomination.objects.select_related('category', 'nominator').order_by('-submitted_at')
    filtered_qs = filter_nominations(qs, category_id=category_id, search_query=search_query, programme=programme)

    if request.GET.get('export') == 'csv':
        AuditEvent.objects.create(
            actor=request.user,
            action='NOMINATIONS_EXPORTED',
            details=f"Exported {filtered_qs.count()} nominations to CSV."
        )
        return export_nominations_to_csv(filtered_qs)

    paginator = Paginator(filtered_qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = AwardCategory.objects.all().order_by('display_order', 'id')

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'programme': programme,
        'total_count': filtered_qs.count(),
    }
    return render(request, 'dashboard/nominations.html', context)


@staff_member_required
def statistics_view(request):
    categories = AwardCategory.objects.filter(is_active=True).order_by('display_order', 'id')
    stats = []

    for cat in categories:
        noms = Nomination.objects.filter(category=cat)
        nom_count = noms.count()

        # Aggregate nominee A names
        names_a = {}
        for nom in noms:
            full_a = f"{nom.nom_a_first} {nom.nom_a_last}".strip().title()
            if full_a:
                names_a[full_a] = names_a.get(full_a, 0) + 1

        top_nominees_a = sorted(names_a.items(), key=lambda x: x[1], reverse=True)[:5]

        # Aggregate nominee B names if gendered/pair
        top_nominees_b = []
        if cat.slot_type in ('gendered', 'pair'):
            names_b = {}
            for nom in noms:
                full_b = f"{nom.nom_b_first} {nom.nom_b_last}".strip().title()
                if full_b:
                    names_b[full_b] = names_b.get(full_b, 0) + 1
            top_nominees_b = sorted(names_b.items(), key=lambda x: x[1], reverse=True)[:5]

        stats.append({
            'category': cat,
            'nom_count': nom_count,
            'top_a': top_nominees_a,
            'top_b': top_nominees_b,
        })

    context = {
        'stats': stats,
        'total_nominations': Nomination.objects.count(),
    }
    return render(request, 'dashboard/statistics.html', context)


@staff_member_required
def name_review_view(request):
    categories = AwardCategory.objects.filter(is_active=True).order_by('display_order', 'id')
    selected_category_id = request.GET.get('category') or (categories.first().id if categories.exists() else None)

    category = None
    variant_groups = []
    unassigned_names = []

    if selected_category_id:
        category = get_object_or_404(AwardCategory, pk=selected_category_id)
        variant_groups = NameVariantGroup.objects.filter(category=category).prefetch_related('variants')

        # Gather all distinct submitted names for this category
        noms = Nomination.objects.filter(category=category)
        names = set()
        for nom in noms:
            name_a = f"{nom.nom_a_first} {nom.nom_a_last}".strip()
            if name_a:
                names.add(name_a)
            name_b = f"{nom.nom_b_first} {nom.nom_b_last}".strip()
            if name_b:
                names.add(name_b)

        # Check which names are already grouped
        grouped_variants = set(
            NameVariant.objects.filter(group__category=category).values_list('submitted_name', flat=True)
        )
        unassigned_names = sorted([n for n in names if n not in grouped_variants])

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_group':
            canonical_name = request.POST.get('canonical_name', '').strip()
            selected_names = request.POST.getlist('selected_names')
            if canonical_name and selected_names and category:
                group = NameVariantGroup.objects.create(
                    category=category,
                    canonical_name=canonical_name,
                    status='same'
                )
                for name in selected_names:
                    NameVariant.objects.create(group=group, submitted_name=name)
                AuditEvent.objects.create(
                    actor=request.user,
                    action='NAME_VARIANTS_MERGED',
                    details=f"Merged {len(selected_names)} variants into '{canonical_name}' for {category.name}."
                )
                messages.success(request, f"Created variant group for '{canonical_name}'.")
        elif action == 'update_status':
            group_id = request.POST.get('group_id')
            new_status = request.POST.get('status')
            if group_id and new_status in ('review', 'same', 'different'):
                group = get_object_or_404(NameVariantGroup, pk=group_id)
                group.status = new_status
                group.save()
                messages.success(request, f"Updated group '{group.canonical_name}' status.")
        return redirect(f"{request.path}?category={selected_category_id}")

    context = {
        'categories': categories,
        'selected_category': category,
        'variant_groups': variant_groups,
        'unassigned_names': unassigned_names,
    }
    return render(request, 'dashboard/name_review.html', context)

