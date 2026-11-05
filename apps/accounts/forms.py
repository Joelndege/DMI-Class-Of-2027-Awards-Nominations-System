from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['programme', 'avatar_url']
        widgets = {
            'programme': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-dark-800 border border-gold-500/30 rounded text-white focus:border-gold-accent outline-none'}),
            'avatar_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 bg-dark-800 border border-gold-500/30 rounded text-white focus:border-gold-accent outline-none'}),
        }

