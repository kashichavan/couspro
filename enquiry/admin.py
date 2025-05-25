from django.contrib import admin
from .models import Counsellor, Enquiry, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1  # Number of empty forms to show
    readonly_fields = ('created_at',)
    fields = ('comment', 'created_at')
    can_delete = True
    show_change_link = False


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'mobile',
        'subject',
        'status',
        'enquiry_type',
        'counsellor',
        'fees_paid',
        'target_fees',
        'fees_balance',
        'is_fully_paid',
        'followup_date',
        'enquiry_date'
    )
    list_filter = (
        'status',
        'subject',
        'enquiry_type',
        'counsellor',
        'followup_date',
    )
    search_fields = ('name', 'mobile', 'counsellor__name')
    readonly_fields = ('fees_balance', 'created_at')  # <-- Add created_at here
    inlines = [CommentInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'mobile', 'parent_number', 'subject', 'status', 'enquiry_type', 'counsellor')
        }),
        ('Course & Fees', {
            'fields': ('target_fees', 'fees_paid', 'fees_balance', 'due_date')
        }),
        ('Dates', {
            'fields': ('enquiry_date', 'followup_date', 'created_at')  # Still okay if readonly
        }),
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Counsellor)
class CounsellorAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'department')
    search_fields = ('name', 'department')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'enquiry_link',
        'comment',
        'created_at',
        'enquiry_status',
        'enquiry_course',
        'enquiry_mobile'
    )
    list_filter = ('created_at',)
    search_fields = (
        'enquiry__name',
        'enquiry__mobile',
        'comment'
    )
    readonly_fields = ('created_at', 'enquiry', 'comment')

    def enquiry_link(self, obj):
        return obj.enquiry.name
    enquiry_link.short_description = 'Enquiry Name'

    def enquiry_mobile(self, obj):
        return obj.enquiry.mobile
    enquiry_mobile.short_description = 'Mobile'

    def enquiry_status(self, obj):
        return obj.enquiry.get_status_display()
    enquiry_status.short_description = 'Status'

    def enquiry_course(self, obj):
        return obj.enquiry.get_subject_display()
    enquiry_course.short_description = 'Course'