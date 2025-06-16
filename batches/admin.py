# admin.py

from django.contrib import admin
from .models import Trainer, Tracker, Batch
from .forms import BatchForm

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')

@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'phone')

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    form = BatchForm
    list_display = ('code', 'subject', 'trainer', 'tracker', 'batch_date', 'created_at')
    search_fields = ('code', 'subject')
    autocomplete_fields = ['trainer', 'tracker']
    filter_horizontal = ['students']
    list_filter = ('trainer', 'tracker', 'batch_date')

    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',)
        }
