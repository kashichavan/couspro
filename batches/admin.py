from django.contrib import admin
from .models import Trainer, Tracker, Batch
from enquiry.models import Enquiry

# Trainer Admin
@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email')
    search_fields = ('name', 'email')
    ordering = ('name',)

# Tracker Admin
@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone')
    search_fields = ('name', 'phone')
    ordering = ('name',)

# Inline for ManyToMany Students in Batch
class EnquiryInline(admin.TabularInline):
    model = Batch.students.through  # Through table for ManyToMany
    extra = 1
    verbose_name = "Assigned Student"
    verbose_name_plural = "Assigned Students"
    autocomplete_fields = ['enquiry']

# Batch Admin
@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'subject', 'trainer', 'tracker', 'created_at')
    list_filter = ('trainer', 'tracker', 'created_at')
    search_fields = ('code', 'subject', 'trainer__name', 'tracker__name')
    ordering = ('-created_at',)
    autocomplete_fields = ['trainer', 'tracker']
    inlines = [EnquiryInline]
    filter_horizontal = ('students',)  # Also enables better UI for ManyToMany if inlines are skipped

    fieldsets = (
        ('Batch Info', {
            'fields': ('code', 'subject', 'trainer', 'tracker', 'remarks')
        }),
        ('Students', {
            'fields': ('students',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at',)
