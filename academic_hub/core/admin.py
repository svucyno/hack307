from django.contrib import admin
from .models import User, Subject, UploadedFile, Timetable, Notification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'role', 'date_joined']
    list_filter = ['role']
    search_fields = ['name', 'email']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'semester', 'teacher']
    list_filter = ['semester']


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'uploaded_by', 'uploaded_at']
    list_filter = ['file_type']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['day', 'subject', 'start_time', 'end_time', 'room']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notif_type', 'recipient', 'is_read', 'created_at']
