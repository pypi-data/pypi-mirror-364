from django.contrib import admin
from .models import NotificationLog

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'sent_from', 'sent_to', 'status', 'sent_at')
    list_filter = ('notification_type', 'status')
    search_fields = ('sent_from', 'sent_to', 'message')
