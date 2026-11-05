from django import forms
from .models import DraftEntry

class DraftEntryForm(forms.ModelForm):
    class Meta:
        model = DraftEntry
        fields = [
            'nom_a_first', 'nom_a_last', 'nom_a_programme',
            'nom_b_first', 'nom_b_last', 'nom_b_programme',
            'skipped'
        ]

