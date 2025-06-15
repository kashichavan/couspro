from django import forms
from .models import Batch, Trainer, Tracker
from enquiry.models import Enquiry

class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Trainer.objects.filter(email=email).exists():
            raise forms.ValidationError("A trainer with this email already exists.")
        return email


class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        fields = ['name', 'phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(phone) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits long.")
        return phone

from django import forms
from .models import Batch, Trainer, Tracker
from enquiry.models import Enquiry
from django.forms.widgets import SelectDateWidget

class BatchForm(forms.ModelForm):
    batch_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Select Batch Date'
        })
    )

    class Meta:
        model = Batch
        fields = ['code', 'subject', 'trainer', 'tracker', 'batch_date', 'remarks']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Batch Code (e.g., PY-JUN-01)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject (e.g., Python Full Stack)'
            }),
            'trainer': forms.Select(attrs={
                'class': 'form-select',
            }),
            'tracker': forms.Select(attrs={
                'class': 'form-select',
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any remarks for this batch...'
            }),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if " " in code:
            raise forms.ValidationError("Batch code should not contain spaces.")
        return code
