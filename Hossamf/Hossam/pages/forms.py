from django import forms
from .models import Npages  # Assuming Npages is your model

class NpagesForm(forms.ModelForm):
    class Meta:
        model = Npages
        fields = ['name', 'email', 'Birth_date', 'phone_number', 'address', 'suger_year', 'type_order',
                  'cumulative_glucose_test', 'heart_diseases', 'blood_pressure', 'cholestrol_level',
                  'smoker', 'Notes', 'image']