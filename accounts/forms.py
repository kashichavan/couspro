from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import CustomUser

class CounselorRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'counselor'
        if commit:
            user.save()
        return user
    


class CustomPasswordChangeForm(PasswordChangeForm):
    pass

# forms.py
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailAuthenticationForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            try:
                # Get user by email
                user = UserModel.objects.get(email=username)
                return user.username  # Use the username internally
            except UserModel.DoesNotExist:
                raise self.get_invalid_login_error()
        return username
    
    
    
# forms.py
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import CustomUser

from django import forms
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role', 'password', 'is_active', 'is_staff', 'is_superuser', 'is_approved')

