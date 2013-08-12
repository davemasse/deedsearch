from django import forms

COUNTIES = {
    'EB': 'cheshire',
    'GB': 'grafton',
    'HB': 'hillsborough',
    'OB': 'coos',
    'RB': 'rockingham',
    'UB': 'sullivan',
}
COUNTY_CHOICES = (
    ('EB', COUNTIES['EB']),
    ('GB', COUNTIES['GB']),
    ('HB', COUNTIES['HB']),
    ('OB', COUNTIES['OB']),
    ('RB', COUNTIES['RB']),
    ('UB', COUNTIES['UB']),
)

class DeedForm(forms.Form):
    county = forms.ChoiceField(choices=COUNTY_CHOICES)
    book = forms.CharField()
    plan = forms.CharField()
