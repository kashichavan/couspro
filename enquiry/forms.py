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
from .models import Enquiry, EducationInfo, Comment  # Added Comment import


class EnquiryForm(forms.ModelForm):
    # Education fields from EducationInfo model
    education_level = forms.ChoiceField(
        choices=EducationInfo.EDUCATION_LEVEL_CHOICES,
        required=True,
        label="Education Level",
        widget=forms.Select()
    )
    ug_degree = forms.ChoiceField(
        choices=EducationInfo.UG_DEGREE_CHOICES,
        required=False,
        label="UG Degree",
        widget=forms.Select()
    )
    other_ug_degree_name = forms.CharField(
        max_length=100,
        required=False,
        label="Other UG Degree Name",
        widget=forms.TextInput()
    )
    pg_degree = forms.ChoiceField(
        choices=EducationInfo.PG_DEGREE_CHOICES,
        required=False,
        label="PG Degree",
        widget=forms.Select()
    )
    other_pg_degree_name = forms.CharField(
        max_length=100,
        required=False,
        label="Other PG Degree Name",
        widget=forms.TextInput()
    )
    branch = forms.CharField(
        max_length=100,
        required=False,
        label="Branch",
        widget=forms.TextInput()
    )
    year_of_passing = forms.IntegerField(
        required=True,
        label="Year of Passing",
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 2024'})
    )
    percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=True,
        label="Percentage",
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 78.50'})
    )

    college_name = forms.CharField(
        max_length=150,
        required=False,
        label='College Name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter college name'})
    )
    college_place = forms.CharField(
        max_length=150,
        required=False,
        label='College Place',
        widget=forms.TextInput(attrs={'placeholder': 'Enter college place'})
    )

    # New comment field
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label='Add Comment (Optional)',
        help_text='Leave this blank if no comment is needed.'
    )

    class Meta:
        model = Enquiry
        fields = [
            'name', 'mobile', 'parent_number', 'native_district_name',
            'subject', 'other_subject_name', 'status', 'enquiry_type',
            'counsellor', 'visit_type', 'followup_date', 'enquiry_date',
            'target_fees', 'fees_paid', 'due_date',
            # Add other relevant fields from your model
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
            'other_subject_name': forms.TextInput(attrs={'placeholder': 'Specify other subject'}),
            'followup_date': forms.DateInput(attrs={'type': 'date'}),
            'enquiry_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply CSS classes
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            else:
                field.widget.attrs.setdefault('class', 'form-control')

        # Set empty labels for dropdowns
        for field_name in ['subject', 'enquiry_type', 'status', 'counsellor', 'visit_type']:
            if field_name in self.fields:
                self.fields[field_name].empty_label = f"Select {self.fields[field_name].label}"

        self.fields['enquiry_date'].required = True
        self.fields['parent_number'].required = False
        self.fields['native_district_name'].required = False

        if self.instance.pk and hasattr(self.instance, 'education_details') and self.instance.education_details.exists():
            edu_info = self.instance.education_details.first()
            self.initial['college_name'] = edu_info.college_name
            self.initial['college_place'] = edu_info.college_place
            self.initial['education_level'] = edu_info.level
            self.initial['ug_degree'] = edu_info.ug_degree
            self.initial['other_ug_degree_name'] = edu_info.other_ug_degree_name
            self.initial['pg_degree'] = edu_info.pg_degree
            self.initial['other_pg_degree_name'] = edu_info.other_pg_degree_name
            self.initial['branch'] = edu_info.branch
            self.initial['year_of_passing'] = edu_info.year_of_passing
            self.initial['percentage'] = edu_info.percentage

    def clean(self):
        cleaned = super().clean()
        subject = cleaned.get('subject')
        status = cleaned.get('status')
        other_subject = cleaned.get('other_subject_name')
        fees_paid = cleaned.get('fees_paid') or Decimal('0.00')
        target_fees = cleaned.get('target_fees') or Decimal('0.00')

        if subject == 'other' and not other_subject:
            self.add_error('other_subject_name', "Please specify the subject name.")

        if status != 'joined':
            cleaned['fees_paid'] = Decimal('0.00')
            cleaned['target_fees'] = None
            cleaned['due_date'] = None
            self._errors.pop('target_fees', None)
            self._errors.pop('fees_paid', None)
            self._errors.pop('due_date', None)
        elif fees_paid > target_fees:
            self.add_error('fees_paid', "Fees paid cannot exceed target fees.")

        # Education level specific validations
        level = cleaned.get('education_level')
        if level == 'ug':
            if not cleaned.get('ug_degree'):
                self.add_error('ug_degree', "UG degree is required.")
            if cleaned.get('ug_degree') == 'other' and not cleaned.get('other_ug_degree_name'):
                self.add_error('other_ug_degree_name', "Specify the UG degree.")
        elif level == 'pg':
            if not cleaned.get('pg_degree'):
                self.add_error('pg_degree', "PG degree is required.")
            if cleaned.get('pg_degree') == 'other' and not cleaned.get('other_pg_degree_name'):
                self.add_error('other_pg_degree_name', "Specify the PG degree.")

        return cleaned

    def save(self, commit=True):
        enquiry = super().save(commit=False)
        status = enquiry.status

        # Fees logic
        if status != 'joined':
            enquiry.fees_paid = Decimal('0.00')
            enquiry.target_fees = None
            enquiry.due_date = None
            enquiry.fees_balance = None
        else:
            if enquiry.target_fees and enquiry.fees_paid:
                enquiry.fees_balance = max(Decimal('0.00'), enquiry.target_fees - enquiry.fees_paid)
                enquiry.fees_paid_date = datetime.today().date()

        if commit:
            enquiry.save()

        # EducationInfo handling
        edu_info = enquiry.education_details.first() if enquiry.education_details.exists() else EducationInfo(enquiry=enquiry)

        edu_info.level = self.cleaned_data.get('education_level')
        edu_info.branch = self.cleaned_data.get('branch', '').upper()
        edu_info.year_of_passing = self.cleaned_data.get('year_of_passing')
        edu_info.percentage = self.cleaned_data.get('percentage')
        edu_info.college_name = self.cleaned_data.get('college_name', '')
        edu_info.college_place = self.cleaned_data.get('college_place', '')

        if edu_info.level == 'ug':
            edu_info.ug_degree = self.cleaned_data.get('ug_degree')
            edu_info.other_ug_degree_name = self.cleaned_data.get('other_ug_degree_name', '')
            edu_info.pg_degree = None
            edu_info.other_pg_degree_name = None
        elif edu_info.level == 'pg':
            edu_info.pg_degree = self.cleaned_data.get('pg_degree')
            edu_info.other_pg_degree_name = self.cleaned_data.get('other_pg_degree_name', '')
            edu_info.ug_degree = None
            edu_info.other_ug_degree_name = None

        if commit:
            edu_info.save()

        # Comment handling
        comment_text = self.cleaned_data.get('comment')
        if comment_text and commit:
            Comment.objects.create(
                enquiry=enquiry,
                comment=comment_text
            )

        return enquiry


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
        
