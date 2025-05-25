from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name='accounts'


urlpatterns = [
   # Use namespace in all URL patterns
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    
    path('reset-password/', views.password_reset_request, name='password_reset'),
    path('reset-password/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset-password/complete/', views.password_reset_complete, name='password_reset_complete'),
    
    
    path('register/counselor/', views.CounselorRegisterView.as_view(), name='counselor_register'),
    path('approve/', views.CounselorApprovalView.as_view(), name='approval_list'),
    path('approve/<int:pk>/', views.ApproveCounselorView.as_view(), name='approve_counselor'),
   path('test-email/', views.test_email_view, name='test_email'),
path('unauthorized/', views.unauthorized, name='unauthorized'),
   ]
