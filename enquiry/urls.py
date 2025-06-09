from django.urls import path
from . import views

app_name = 'enquiry'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Enquiry CRUD & Details
    path('add-enquiry/', views.add_enquiry, name='add_enquiry'),
    path('enquiry-success/', views.enquiry_success, name='enquiry_success'),
    path('enquiry/<int:enquiry_id>/', views.enquiry_details, name='enquiry_details'),
    path('enquiry/<int:pk>/edit/', views.edit_enquiry, name='edit_enquiry'),
    path('enquiry-list/', views.EnquiryListView.as_view(), name='enquary_list'),
    
    # Counsellor
    path('add-counsellor/', views.add_counsellor, name='add_counsellor'),
    path('counsellor-success/', views.counsellor_success, name='counsellor_success'),
    
    # Follow-ups
    path('today-followups/', views.today_followups, name='today_followups'),
    path('followups/today/', views.today_followups, name='today_followups'),
    path('followups/update-comment/', views.update_comment, name='update_comment'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('get-comments/', views.get_comments, name='get_comments'),
    path('update-followup-date/', views.update_followup_date, name='update_followup_date'),
    path('update-status/', views.update_status, name='update_status'),
    
    # Calendar
    path('get-calendar-data/', views.get_calendar_data, name='get_calendar_data'),
     path('get-fees-details/<int:enquiry_id>/', views.get_fees_details, name='get_fees_details'),
    # Students
    path('joined-students/', views.joined_students, name='joined_students'),
    path('dropout-students/', views.dropout_students, name='dropout_students'),
    path('pending-enquiries/', views.pending_enquiries, name='pending_enquiries'),
    path('today-enquiries/', views.today_enquiries, name='today_enquiries'),
    
    # Bulk Upload
    path('download-template/', views.download_dummy_template, name='download_dummy_template'),
    path('bulk-upload/', views.bulk_enquiry_upload, name='bulk_enquiry_upload'),
    
    # Monthly Reports
    path('monthly-students/', views.monthly_student_list, name='monthly_student_list'),
    path('monthly-students/download-excel/', views.download_monthly_excel, name='download_monthly_excel'),
    
    path('monthly-summary/', views.monthly_summary_dashboard, name='monthly_summary_dashboard'),
    path('monthly-summary/download/', views.download_monthly_summary_excel, name='download_monthly_summary_excel'),
    
    path('monthly-summary/counsellor/', views.monthly_summary_by_counsellor, name='monthly_summary_by_counsellor'),
    path('monthly-summary/counsellor/download/', views.download_monthly_summary_by_counsellor_excel, name='download_monthly_summary_by_counsellor_excel'),
    path('monthly-summary/counsellor/<int:counsellor_id>/<int:year>/<int:month>/', views.counsellor_monthly_details, name='counsellor_monthly_details'),
    
    # Payment Dues
    path('payment-due/today/', views.payment_due_list, {'due_type': 'today'}, name='today_payment_due'),
    path('payment-due/past/', views.payment_due_list, {'due_type': 'past'}, name='past_payment_due'),
    path('payment-due/export/<str:due_type>/', views.export_payment_due_csv, name='export_payment_due'),
    path('update-due-date/', views.update_due_date, name='update_due_date'),
    path('enquiry/update-payment/', views.update_payment, name='update_payment'),
    
    
    
    path('calendar-data/', views.get_calendar_data, name='get_calendar_data'),
    path('followups/', views.get_followups, name='get_followups'),
    path('check-mobile-exists/', views.check_mobile_exists, name='check_mobile_exists'),
    path('daywise-summary/', views.daywise_counsellor_summary, name='daywise_summary'),
    path('export-enquiries/', views.export_enquiries_view, name='export_todays_enquiries'),
    
    
    path('target/add/', views.MonthlyTargetCreateView.as_view(), name='monthly_target_add'),
    path('target/<int:target_id>/edit/', views.MonthlyTargetUpdateView.as_view(), name='monthly_target_edit'),

    path('due-fees-calendar/', views.due_fees_calendar_view, name='due_fees_calendar'),
    path('ajax/get-due-fees-data/', views.due_fees_data_ajax, name='ajax_due_fees_data'),

     path('update-education/', views.update_education, name='update_education'),
    path('update-target-fees/', views.update_target_fees, name='update_target_fees'),
    path('inconsistent-joined/', views.InconsistentJoinedEnquiryListView.as_view(), name='inconsistent_joined'),
    path('enquiry/<int:pk>/mark-joined/', views.mark_joined_batch, name='mark_joined_batch'),

]
