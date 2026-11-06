from django import forms
from .models import PlanSet

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='Search plans')
