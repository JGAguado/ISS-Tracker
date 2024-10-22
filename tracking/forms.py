from django import forms

class UserLocationForm(forms.Form):
    latitude = forms.FloatField(label='Your Latitude', min_value=-90, max_value=90)
    longitude = forms.FloatField(label='Your Longitude', min_value=-180, max_value=180)
