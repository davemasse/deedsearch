from django import forms

from .utils import Deed, COUNTY_CHOICES, INDEX


class DeedForm(forms.Form):
    county = forms.ChoiceField(choices=COUNTY_CHOICES)
    book = forms.CharField()
    plan = forms.CharField()

    def clean(self):
        cleaned_data = super(DeedForm, self).clean()

        deed = Deed(county=self.cleaned_data.get('county'), book=self.cleaned_data.get('book'), plan=self.cleaned_data.get('plan'))

        if not deed.is_valid():
            raise forms.ValidationError('The record you requested is not available.')

class DeedSearchForm(forms.Form):
    county = forms.ChoiceField(choices=COUNTY_CHOICES)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    index = forms.ChoiceField(choices=INDEX)
