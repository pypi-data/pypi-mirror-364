from django import forms
from .models import Tache

class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = ['titre', 'description', 'terminee']
