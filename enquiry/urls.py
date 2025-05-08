from django.urls import path
from . import views

app_name='enquiry'


urlpatterns = [
    path('add-enquiry/', views.add_enquiry, name='add_enquiry'),  # URL for adding enquiry
    path('enquiry-success/', views.enquiry_success, name='enquiry_success'),  # Redirect after success
    
     path('add-counsellor/', views.add_counsellor, name='add_counsellor'),  # URL for adding counsellor
    path('counsellor-success/', views.counsellor_success, name='counsellor_success'),
    path('followups/today/', views.today_followups, name='today_followups'),
    path('followups/update-comment/', views.update_comment, name='update_comment'),
     path('add_comment/', views.add_comment, name='add_comment'),
     path('get-comments/', views.get_comments, name='get_comments'),
    
   
    path('', views.dashboard, name='dashboard'),
    path('today-followups/', views.today_followups, name='today_followups'),
    path('get-calendar-data/', views.get_calendar_data, name='get_calendar_data'),
    path('update-followup-date/', views.update_followup_date, name='update_followup_date'),
    path('update-status/', views.update_status, name='update_status'),
    
     path('joined-students/', views.joined_students, name='joined_students'),
    path('dropout-students/', views.dropout_students, name='dropout_students'),
    path('pending-enquiries/', views.pending_enquiries, name='pending_enquiries'),
    
    path('enquiry/<int:enquiry_id>/', views.enquiry_details, name='enquiry_details'),
    path('enquiry-list/',views.EnquiryListView.as_view(),name='enquary_list'),
    path('download-template/', views.download_dummy_template, name='download_dummy_template'),
    path('bulk-upload/', views.bulk_enquiry_upload, name='bulk_enquiry_upload'),
]
