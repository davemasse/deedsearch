from django import forms

COUNTIES = {
    'EB': 'Cheshire',
    'GB': 'Grafton',
    'HB': 'Hillsborough',
    'OB': 'Coos',
    'RB': 'Rockingham',
    'UB': 'Sullivan',
}
COUNTY_CHOICES = (
    ('EB', COUNTIES['EB']),
    ('GB', COUNTIES['GB']),
    ('HB', COUNTIES['HB']),
    ('OB', COUNTIES['OB']),
    ('RB', COUNTIES['RB']),
    ('UB', COUNTIES['UB']),
)

from .utils import Deed

class DeedForm(forms.Form):
    county = forms.ChoiceField(choices=COUNTY_CHOICES)
    book = forms.CharField()
    plan = forms.CharField()

    def clean(self):
        cleaned_data = super(DeedForm, self).clean()

        deed = Deed(county=self.cleaned_data.get('county'), book=self.cleaned_data.get('book'), plan=self.cleaned_data.get('plan'))

        if not deed.is_valid():
            raise forms.ValidationError('The record you requested is not available.')
