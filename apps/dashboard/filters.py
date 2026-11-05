from apps.nominations.models import Nomination

def filter_nominations(queryset, category_id=None, search_query=None, programme=None):
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if search_query:
        from django.db.models import Q
        q = search_query.strip()
        queryset = queryset.filter(
            Q(nom_a_first__icontains=q) |
            Q(nom_a_last__icontains=q) |
            Q(nom_b_first__icontains=q) |
            Q(nom_b_last__icontains=q) |
            Q(nominator__email__icontains=q) |
            Q(nominator__username__icontains=q)
        )
    if programme:
        from django.db.models import Q
        p = programme.strip()
        queryset = queryset.filter(
            Q(nom_a_programme__icontains=p) |
            Q(nom_b_programme__icontains=p)
        )
    return queryset

