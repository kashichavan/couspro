from datetime import datetime
from django import forms
from .models import Enquiry,Counsellor,Comment

from django import forms
from .models import Enquiry, Counsellor

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        
from django import forms
from .models import CollegeInfo




from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

class EnquiryForm(forms.ModelForm):
    college_name = forms.CharField(
        max_length=150,
        required=False,
        label='College Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter college name'})
    )
    college_place = forms.CharField(
        max_length=150,
        required=False,
        label='College Place',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter college place'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate initial values for college fields
        if self.instance and self.instance.college:
            self.fields['college_name'].initial = self.instance.college.college_name
            self.fields['college_place'].initial = self.instance.college.college_place

        # Add bootstrap classes
        for field_name, field in self.fields.items():
            if field_name not in ['college_name', 'college_place']:
                widget_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
                field.widget.attrs.update({'class': widget_class})

        # Set empty labels for choice fields
        self.fields['subject'].empty_label = 'Select Course'
        self.fields['enquiry_type'].empty_label = 'Select Enquiry Type'
        self.fields['status'].empty_label = 'Select Status'
        self.fields['counsellor'].empty_label = 'Select Counsellor'
        self.fields['visit_type'].empty_label = 'Select Visit Type'

        # Conditionally require fees fields only if status is 'joined'
        initial_status = self.initial.get('status', getattr(self.instance, 'status', None))
        if initial_status != 'joined':
            for field in ['target_fees', 'fees_paid', 'due_date']:
                self.fields[field].required = False

        self.fields['enquiry_date'].required = True
        self.fields['parent_number'].required = False
        self.fields['native_district_name'].required = False
        
        

        

    class Meta:
        model = Enquiry
        fields = [
            'name',
            'mobile',
            'parent_number',
            'native_district_name',
            'subject',
            'other_subject_name',
            'status',
            'enquiry_type',
            'counsellor',
            'visit_type',
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
            'native_district_name': 'Native District',
            'subject': 'Course',
            'other_subject_name': 'Other Subject Name',
            'status': 'Current Status',
            'enquiry_type': 'Enquiry Mode',
            'counsellor': 'Assigned Counsellor',
            'visit_type': 'Visit Type',
            'followup_date': 'Follow-Up Date',
            'enquiry_date': 'Enquiry Date',
            'target_fees': 'Target Fees',
            'fees_paid': 'Fees Paid',
            'due_date': 'Due Date',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter full name'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter mobile number'}),
            'parent_number': forms.TextInput(attrs={'placeholder': 'Enter parent number'}),
            'native_district_name': forms.TextInput(attrs={'placeholder': 'Enter native district'}),
            'followup_date': forms.DateInput(attrs={'type': 'date'}),
            'enquiry_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'other_subject_name': forms.TextInput(attrs={'placeholder': 'Specify other subject'}),
        }

    # forms.py
    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        other_subject_name = cleaned_data.get('other_subject_name')
        status = cleaned_data.get('status')
        fees_paid = cleaned_data.get('fees_paid')
        target_fees = cleaned_data.get('target_fees')

        # Validate other_subject_name
        if subject == 'other' and not other_subject_name:
            self.add_error('other_subject_name', "Please specify the subject when 'Other' is selected.")

        # Handle fees_paid when status is not 'joined'
        if status != 'joined':
            # Set fees_paid to 0.00 if status is not joined
            cleaned_data['fees_paid'] = Decimal('0.00')
            
            # Clear other fee-related fields
            cleaned_data['target_fees'] = None
            cleaned_data['due_date'] = None
        else:
            # Validate fees_paid <= target_fees
            if target_fees is not None and fees_paid is not None:
                if fees_paid > target_fees:
                    self.add_error('fees_paid', "Fees paid cannot exceed target fees.")
                    
        return cleaned_data

        # forms.py
    def save(self, commit=True):
        # Handle CollegeInfo
        college_name = self.cleaned_data.get('college_name')
        college_place = self.cleaned_data.get('college_place')

        college_instance = None
        if college_name:
            college_instance, created = CollegeInfo.objects.get_or_create(
                college_name=college_name,
                defaults={'college_place': college_place}
            )
            if not created and college_place and college_instance.college_place != college_place:
                college_instance.college_place = college_place
                college_instance.save()

        enquiry_instance = super().save(commit=False)
        enquiry_instance.college = college_instance

        # Handle fees based on status
        if enquiry_instance.status != 'joined':
            enquiry_instance.target_fees = None
            enquiry_instance.fees_paid = Decimal('0.00')
            enquiry_instance.fees_balance = None
            enquiry_instance.due_date = None
        else:
            # Recalculate fees_balance
            target_fees = enquiry_instance.target_fees
            fees_paid = enquiry_instance.fees_paid

            if target_fees is not None and fees_paid is not None:
                if fees_paid > target_fees:
                    enquiry_instance.fees_paid = target_fees
                    enquiry_instance.fees_balance = Decimal('0.00')
                else:
                    enquiry_instance.fees_balance = target_fees - fees_paid
                enquiry_instance.fees_paid_date = datetime.today().date()

        if commit:
            enquiry_instance.save()

        return enquiry_instance




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
    
    
    
# forms.py
from django import forms
from .models import MonthlyTarget

class MonthlyTargetForm(forms.ModelForm):
    class Meta:
        model = MonthlyTarget
        fields = ['month', 'year', 'target_amount']
        widgets = {
            'month': forms.Select(choices=MonthlyTarget.MONTH_CHOICES),
            'year': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
            'target_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['month'].widget.attrs.update({'class': 'form-control'})
        self.fields['year'].widget.attrs.update({'class': 'form-control'})
        self.fields['target_amount'].widget.attrs.update({'class': 'form-control'})