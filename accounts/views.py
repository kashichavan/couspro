from django.views.generic import ListView, View, CreateView
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect,render
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import CustomUser
from .forms import CounselorRegistrationForm, CustomPasswordChangeForm, EmailAuthenticationForm
# views.py
from django.contrib.auth.views import LoginView
# accounts/views.py
from django.shortcuts import render

def unauthorized(request):
    """
    View to display an unauthorized access message.
    This view does not require login, as it may be shown to unauthenticated users.
    """
    return render(request, 'registration/unauthorized.html')



from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

def test_email_view(request):
    subject = 'Test Email from Django'
    message = 'This is a test email sent from your Django project.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['kashichavan7777@gmail.com']  # Replace with your actual email

    try:
        send_mail(subject, message, from_email, recipient_list)
        return HttpResponse('✅ Test email sent successfully!')
    except Exception as e:
        return HttpResponse(f'❌ Failed to send email: {e}')


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('enquiry:dashboard')

    def form_valid(self, form):
        user = form.get_user()
        if user.role == 'counselor' and not user.is_approved:
            messages.error(self.request, 'Your account is pending approval.')
            return redirect('accounts:login')
        return super().form_valid(form)

class CounselorRegisterView(CreateView):
    form_class = CounselorRegistrationForm
    template_name = 'registration/counselor_register.html'
    success_url = reverse_lazy('accounts:login')

class CounselorApprovalView(UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'registration/approval_list.html'
    context_object_name = 'pending_counselors'

    def test_func(self):
        return self.request.user.role == 'manager' and self.request.user.is_approved

    def get_queryset(self):
        return CustomUser.objects.filter(role='counselor', is_approved=False)

class ApproveCounselorView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'manager' and self.request.user.is_approved

    def post(self, request, pk):
        counselor = get_object_or_404(CustomUser, pk=pk)
        counselor.is_approved = True
        counselor.save()
        messages.success(request, f'{counselor.email} has been approved.')
        return redirect('accounts:approval_list')

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('accounts:password_change_done')
    
    
    
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse

User = get_user_model()

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'registration/password_reset_done.html')

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(
            reverse_lazy('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

        subject = "Password Reset Request"
        message = f"Click the link below to reset your password:\n{reset_url}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return render(request, 'registration/password_reset_done.html')
    return render(request, 'registration/password_reset_form.html')
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.urls import reverse
import json
import re

User = get_user_model()

@csrf_protect
@require_http_methods(["GET", "POST"])
def password_reset_confirm(request, uidb64, token):
    """
    Handle password reset confirmation with AJAX support
    """
    try:
        # Decode the user ID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Verify the token
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            # Handle AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return handle_ajax_password_reset(request, user)
            else:
                # Handle regular form submission
                return handle_regular_password_reset(request, user)
        else:
            # GET request - show the form
            return render(request, 'registration/password_reset_confirm.html', {
                'validlink': True,
                'user': user
            })
    else:
        # Invalid link
        return render(request, 'accounts/password_reset_confirm.html', {
            'validlink': False,
            'error': 'The password reset link is invalid or has expired.'
        })

def handle_ajax_password_reset(request, user):
    """
    Handle AJAX password reset request
    """
    try:
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate passwords match
        if password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Passwords do not match.'
            })
        
        # Validate password strength
        validation_result = validate_password_strength(password)
        if not validation_result['is_valid']:
            return JsonResponse({
                'success': False,
                'message': 'Password does not meet security requirements.',
                'validation_errors': validation_result['errors']
            })
        
        # Set the new password
        user.set_password(password)
        user.save()
        
        # Log the user out of all sessions (optional security measure)
        # This forces them to log in with the new password
        from django.contrib.sessions.models import Session
        from django.utils import timezone
        
        # Optional: Clear all user sessions
        # for session in Session.objects.all():
        #     session_data = session.get_decoded()
        #     if session_data.get('_auth_user_id') == str(user.id):
        #         session.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Password has been reset successfully!',
            'redirect_url': reverse('accounts:login')
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while resetting your password. Please try again.'
        })

def handle_regular_password_reset(request, user):
    """
    Handle regular form submission (non-AJAX)
    """
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')
    
    # Validate passwords match
    if password != confirm_password:
        messages.error(request, 'Passwords do not match.')
        return render(request, 'accounts/password_reset_confirm.html', {
            'validlink': True,
            'user': user,
            'error': 'Passwords do not match.'
        })
    
    # Validate password strength
    validation_result = validate_password_strength(password)
    if not validation_result['is_valid']:
        messages.error(request, 'Password does not meet security requirements.')
        return render(request, 'accounts/password_reset_confirm.html', {
            'validlink': True,
            'user': user,
            'error': 'Password does not meet security requirements.'
        })
    
    # Set the new password
    user.set_password(password)
    user.save()
    
    messages.success(request, 'Your password has been reset successfully! You can now log in with your new password.')
    return redirect('accounts:login')

def validate_password_strength(password):
    """
    Validate password strength according to requirements
    """
    errors = []
    
    # Check length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter.")
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter.")
    
    # Check for digit
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number.")
    
    # Check for special character
    if not re.search(r'[@$!%*?&]', password):
        errors.append("Password must contain at least one special character (@$!%*?&).")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

# Optional: AJAX endpoint for real-time password validation
@csrf_protect
def validate_password_ajax(request):
    """
    AJAX endpoint for real-time password validation
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            password = data.get('password', '')
            
            validation_result = validate_password_strength(password)
            
            # Calculate strength
            strength_score = 0
            if len(password) >= 8:
                strength_score += 1
            if re.search(r'[A-Z]', password):
                strength_score += 1
            if re.search(r'[a-z]', password):
                strength_score += 1
            if re.search(r'\d', password):
                strength_score += 1
            if re.search(r'[@$!%*?&]', password):
                strength_score += 1
            
            strength_levels = ['weak', 'weak', 'fair', 'good', 'strong']
            strength = strength_levels[min(strength_score, 4)]
            
            return JsonResponse({
                'is_valid': validation_result['is_valid'],
                'errors': validation_result['errors'],
                'strength': strength,
                'validation': {
                    'length': len(password) >= 8,
                    'uppercase': bool(re.search(r'[A-Z]', password)),
                    'lowercase': bool(re.search(r'[a-z]', password)),
                    'number': bool(re.search(r'\d', password)),
                    'special': bool(re.search(r'[@$!%*?&]', password))
                }
            })
        except Exception as e:
            return JsonResponse({
                'is_valid': False,
                'errors': ['An error occurred during validation.']
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')
