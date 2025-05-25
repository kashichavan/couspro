from django import forms
from .models import Enquiry,Counsellor,Comment

from django import forms
from .models import Enquiry, Counsellor

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
from django import forms
from .models import Enquiry
import re
from django.core.exceptions import ValidationError
from datetime import date

class EnquiryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap classes to widgets
        for field_name, field in self.fields.items():
            widget_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.update({'class': widget_class})

        # Dropdown placeholders
        self.fields['subject'].empty_label = 'Select Course'
        self.fields['enquiry_type'].empty_label = 'Select Enquiry Type'
        self.fields['status'].empty_label = 'Select Status'
        self.fields['counsellor'].empty_label = 'Select Counsellor'

        # Set fees-related fields optional unless joined
        initial_status = self.initial.get('status', getattr(self.instance, 'status', None))
        if initial_status != 'joined':
            for field in ['target_fees', 'fees_paid', 'due_date']:
                self.fields[field].required = False

        # Make enquiry_date required always
        self.fields['enquiry_date'].required = True
        
        self.fields['parent_number'].required = False

    class Meta:
        model = Enquiry
        fields = [
            'name',
            'mobile',
            'parent_number',
            'subject',
            'status',
            'enquiry_type',
            'counsellor',
            'followup_date',
            'enquiry_date',
            'target_fees',
            'fees_paid',
            'due_date',
        ]
        labels = {
            'name': 'Full Name',
            'mobile': 'Contact Number',
            'parent_number': 'Parent Contact Number',
            'subject': 'Course',
            'status': 'Current Status',
            'enquiry_type': 'Enquiry Mode',
            'counsellor': 'Assigned Counsellor',
            'followup_date': 'Follow-Up Date',
            'enquiry_date': 'Enquiry Date',
            'target_fees': 'Target Fees',
            'fees_paid': 'Fees Paid',
            'due_date': 'Due Date',
        }
        help_texts = {
            'subject': 'Select the course the student is interested in.',
            'counsellor': 'Choose the counsellor handling the enquiry.',
            'target_fees': 'Total course fees',
            'fees_paid': 'Amount paid so far',
            'due_date': 'Deadline for full payment',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter full name'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter mobile number'}),
            'parent_number': forms.TextInput(attrs={'placeholder': 'Enter parent number'}),
            'followup_date': forms.DateInput(attrs={'type': 'date'}),
            'enquiry_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile and not re.match(r'^(\+91[\-\s]?)?[6-9]\d{9}$', mobile):
            raise ValidationError("Enter a valid 10-digit Indian mobile number.")
        return mobile

    def clean_parent_number(self):
        parent_number = self.cleaned_data.get('parent_number')
        if parent_number and not re.match(r'^(\+91[\-\s]?)?[6-9]\d{9}$', parent_number):
            raise ValidationError("Enter a valid 10-digit Indian parent contact number.")
        return parent_number

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        target = cleaned_data.get('target_fees')
        paid = cleaned_data.get('fees_paid')
        due = cleaned_data.get('due_date')
        enquiry_date = cleaned_data.get('enquiry_date')

        errors = {}

        # enquiry_date required
        if not enquiry_date:
            errors['enquiry_date'] = ValidationError("Enquiry date is mandatory.")

        if status == 'joined':
            for field in ['target_fees', 'fees_paid', 'due_date']:
                if not cleaned_data.get(field):
                    errors[field] = ValidationError(f"{field.replace('_', ' ').title()} is required when status is 'Joined'.")

        # fees_paid must not exceed target_fees
        if target is not None and paid is not None and paid > target:
            errors['fees_paid'] = ValidationError("Fees paid cannot exceed target fees.")

        # due_date cannot be before enquiry_date
        if due and enquiry_date and due < enquiry_date:
            errors['due_date'] = ValidationError("Due date cannot be earlier than enquiry date.")

        if errors:
            raise ValidationError(errors)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Calculate fees_balance
        if instance.target_fees is not None and instance.fees_paid is not None:
            instance.fees_balance = max(instance.target_fees - instance.fees_paid, 0)
        else:
            instance.fees_balance = None

        if commit:
            instance.save()

        return instance


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