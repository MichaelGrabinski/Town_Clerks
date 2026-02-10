from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'username', 'event_type', 'method', 'status_code', 'path', 'ip_address')
    list_filter = ('event_type', 'method', 'status_code', 'created_at')
    search_fields = ('username', 'path', 'ip_address', 'user_agent', 'referer', 'query_string')
    ordering = ('-created_at',)
from .models import VetRecord, TransmitelReport

@admin.register(VetRecord)
class VetRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'imported_at')

@admin.register(TransmitelReport)
class TransmitelReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'filename', 'imported_at')
