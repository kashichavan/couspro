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
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime
from .models import Enquiry, EducationInfo


class EnquiryForm(forms.ModelForm):
    # Existing college fields (optional)
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

    # EducationInfo fields
    education_level = forms.ChoiceField(
        choices=EducationInfo.EDUCATION_LEVEL_CHOICES,
        required=True,
        label="Education Level",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    ug_degree = forms.ChoiceField(
        choices=EducationInfo.UG_DEGREE_CHOICES,
        required=False,
        label="UG Degree",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    other_ug_degree_name = forms.CharField(
        max_length=100,
        required=False,
        label="Other UG Degree Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    pg_degree = forms.ChoiceField(
        choices=EducationInfo.PG_DEGREE_CHOICES,
        required=False,
        label="PG Degree",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    other_pg_degree_name = forms.CharField(
        max_length=100,
        required=False,
        label="Other PG Degree Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    branch = forms.CharField(
        max_length=100,
        required=False,
        label="Branch",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    year_of_passing = forms.IntegerField(
        required=True,
        label="Year of Passing",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024'})
    )
    percentage = forms.DecimalField(
        max_digits=5, decimal_places=2,
        required=True,
        label="Percentage",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 78.50'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['college_name', 'college_place']:
                widget_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
                field.widget.attrs.update({'class': widget_class})
        self.fields['subject'].empty_label = 'Select Course'
        self.fields['enquiry_type'].empty_label = 'Select Enquiry Type'
        self.fields['status'].empty_label = 'Select Status'
        self.fields['counsellor'].empty_label = 'Select Counsellor'
        self.fields['visit_type'].empty_label = 'Select Visit Type'

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
            'name', 'mobile', 'parent_number', 'native_district_name',
            'subject', 'other_subject_name', 'status', 'enquiry_type', 'counsellor', 'visit_type',
            'followup_date', 'enquiry_date', 'target_fees', 'fees_paid', 'due_date',
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
            cleaned_data['fees_paid'] = Decimal('0.00')
            cleaned_data['target_fees'] = None
            cleaned_data['due_date'] = None
        else:
            if target_fees is not None and fees_paid is not None:
                if fees_paid > target_fees:
                    self.add_error('fees_paid', "Fees paid cannot exceed target fees.")

        # Validate EducationInfo fields
        level = cleaned_data.get('education_level')
        ug_degree = cleaned_data.get('ug_degree')
        other_ug_degree_name = cleaned_data.get('other_ug_degree_name')
        pg_degree = cleaned_data.get('pg_degree')
        other_pg_degree_name = cleaned_data.get('other_pg_degree_name')

        if level == 'ug':
            if not ug_degree:
                self.add_error('ug_degree', "UG degree must be selected for undergraduate level.")
            if ug_degree == 'other' and not other_ug_degree_name:
                self.add_error('other_ug_degree_name', "Please specify the UG degree name when 'Other UG' is selected.")
        elif level == 'pg':
            if not pg_degree:
                self.add_error('pg_degree', "PG degree must be selected for postgraduate level.")
            if pg_degree == 'other' and not other_pg_degree_name:
                self.add_error('other_pg_degree_name', "Please specify the PG degree name when 'Other PG' is selected.")

        return cleaned_data

    def save(self, commit=True):
        enquiry_instance = super().save(commit=False)

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
        enquiry_instance.college = college_instance

        # Fees logic
        if enquiry_instance.status != 'joined':
            enquiry_instance.target_fees = None
            enquiry_instance.fees_paid = Decimal('0.00')
            enquiry_instance.fees_balance = None
            enquiry_instance.due_date = None
        else:
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

        # Save EducationInfo
        level = self.cleaned_data.get('education_level')
        ug_degree = self.cleaned_data.get('ug_degree')
        other_ug_degree_name = self.cleaned_data.get('other_ug_degree_name')
        pg_degree = self.cleaned_data.get('pg_degree')
        other_pg_degree_name = self.cleaned_data.get('other_pg_degree_name')
        branch = self.cleaned_data.get('branch')  # Get branch value
        year_of_passing = self.cleaned_data.get('year_of_passing')
        percentage = self.cleaned_data.get('percentage')

        edu_info = None
        if hasattr(enquiry_instance, 'education_details') and enquiry_instance.education_details.exists():
            edu_info = enquiry_instance.education_details.first()
        if not edu_info:
            edu_info = EducationInfo(enquiry=enquiry_instance)

        edu_info.level = level

        if level == 'ug':
            edu_info.ug_degree = ug_degree
            edu_info.other_ug_degree_name = other_ug_degree_name
            edu_info.pg_degree = None
            edu_info.other_pg_degree_name = None
        elif level == 'pg':
            edu_info.pg_degree = pg_degree
            edu_info.other_pg_degree_name = other_pg_degree_name
            edu_info.ug_degree = None
            edu_info.other_ug_degree_name = None

        # Ensure branch is stored in uppercase
        edu_info.branch = branch.upper() if branch else branch

        edu_info.college_name = college_name or ''
        edu_info.college_place = college_place or ''
        edu_info.year_of_passing = year_of_passing
        edu_info.percentage = percentage

        edu_info.save()

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