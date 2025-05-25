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

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                return redirect('accounts:password_reset_complete')
            else:
                return render(request, 'registration/password_reset_confirm.html', {'error': 'Passwords do not match'})
        return render(request, 'registration/password_reset_confirm.html')
    return HttpResponse("Invalid reset link")

def password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')
