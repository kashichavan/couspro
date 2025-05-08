# admin.py
from django.contrib import admin
from .models import Enquiry, Counsellor, Comment

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile', 'subject', 'status', 'counsellor', 'followup_date', 'created_at']
    list_filter = ['status', 'subject', 'counsellor', 'followup_date']
    search_fields = ['name', 'mobile']

@admin.register(Counsellor)
class CounsellorAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile', 'department']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['enquiry', 'comment', 'created_at']
    search_fields = ['enquiry__name', 'comment']


