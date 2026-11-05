import csv
from django.http import HttpResponse

def export_nominations_to_csv(queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="nominations_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID',
        'Category',
        'Slot Type',
        'Nominee A (First)',
        'Nominee A (Last)',
        'Nominee A (Programme)',
        'Nominee B (First)',
        'Nominee B (Last)',
        'Nominee B (Programme)',
        'Nominator Email',
        'Submitted At',
    ])

    for nom in queryset.select_related('category', 'nominator'):
        writer.writerow([
            nom.id,
            nom.category.name,
            nom.category.get_slot_type_display(),
            nom.nom_a_first,
            nom.nom_a_last,
            nom.nom_a_programme,
            nom.nom_b_first,
            nom.nom_b_last,
            nom.nom_b_programme,
            nom.nominator.email or nom.nominator.username,
            nom.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response

