from django import forms
from .models import Enquiry, Counsellor

class EnquiryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        # Add custom placeholder (optional for CharField choices)
        self.fields['subject'].empty_label = None
        self.fields['enquiry_type'].empty_label = None

    class Meta:
        model = Enquiry
        fields = [
            'name', 'mobile', 'subject', 'status', 'enquiry_type',
            'counsellor', 'followup_date'
        ]
        labels = {
            'name': 'Full Name',
            'mobile': 'Contact Number',
            'subject': 'Select Course',
            'status': 'Status',
            'enquiry_type': 'Enquiry Type',
            'counsellor': 'Select Counsellor',
            'followup_date': 'Follow-up Date',
        }
        help_texts = {
            'subject': 'Choose the course you are interested in',
            'counsellor': 'Choose a counsellor from the list',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter full name'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter mobile number'}),
            'followup_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CounsellorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap styling to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Counsellor
        fields = ['name', 'mobile', 'department']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': ''}),
            'mobile': forms.TextInput(attrs={'placeholder': ''}),
            'department': forms.TextInput(attrs={'placeholder': ''}),
        }
        labels = {
            'mobile': 'Contact Number',
            'department': 'Department'
        }
        
# forms.py
from django import forms

class BulkEnquiryForm(forms.Form):
    excel_file = forms.FileField(label='Select Excel File')