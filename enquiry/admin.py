from django.contrib import admin
from .models import Counsellor, Enquiry, Comment, EducationInfo, PaymentHistory, MonthlyTarget


# Inline Admins
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('comment', 'created_at')
    can_delete = True
    show_change_link = False


class EducationInfoInline(admin.StackedInline):
    model = EducationInfo
    can_delete = False
    verbose_name_plural = 'Education Info'
    fk_name = 'enquiry'  # Explicit foreign key reference if needed
    extra = 1


class PaymentHistoryInline(admin.TabularInline):
    model = PaymentHistory
    extra = 0
    readonly_fields = ('payment_date',)
    fields = ('amount_paid', 'payment_date', 'note')
    can_delete = False


# Main Admin Classes
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
        'enquiry_date',
        'visit_type',
    )
    list_filter = (
        'status',
        'subject',
        'enquiry_type',
        'counsellor',
        'followup_date',
        'visit_type',
    )
    search_fields = ('name', 'mobile', 'counsellor__name')
    readonly_fields = ('fees_balance', 'created_at', 'fees_paid_date')
    inlines = [CommentInline, EducationInfoInline, PaymentHistoryInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'mobile', 'parent_number', 'subject', 'other_subject_name', 'status', 'enquiry_type', 'counsellor', 'visit_type')
        }),
        ('Course & Fees', {
            'fields': ('target_fees', 'fees_paid', 'fees_balance', 'due_date', 'fees_paid_date')
        }),
        ('Dates', {
            'fields': ('enquiry_date', 'followup_date', 'joined_date', 'created_at')
        }),
        ('Batch Info', {
            'fields': ('is_joined_batch',)
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


@admin.register(EducationInfo)
class EducationInfoAdmin(admin.ModelAdmin):
    list_display = (
        'enquiry',
        'level',
        'degree_display',
        'college_name',
        'year_of_passing',
        'percentage'
    )
    search_fields = ('enquiry__name', 'college_name', 'year_of_passing')
    readonly_fields = ('degree_display',)

    def degree_display(self, obj):
        if obj.level == 'ug':
            if obj.ug_degree == 'other':
                return obj.other_ug_degree_name
            else:
                return obj.get_ug_degree_display()
        elif obj.level == 'pg':
            if obj.pg_degree == 'other':
                return obj.other_pg_degree_name
            else:
                return obj.get_pg_degree_display()
    degree_display.short_description = 'Degree'


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('enquiry', 'amount_paid', 'payment_date', 'note')
    list_filter = ('payment_date',)
    search_fields = ('enquiry__name', 'note')
    readonly_fields = ('payment_date',)


@admin.register(MonthlyTarget)
class MonthlyTargetAdmin(admin.ModelAdmin):
    list_display = ('month', 'year', 'target_amount', 'actual_collected', 'remaining')
    list_filter = ('year', 'month')
    search_fields = ['year', 'month']