from django.contrib import admin
from .models import Task, UserProfile

def reset_notification(modeladmin, request, queryset):
    queryset.update(is_notified=False)
    modeladmin.message_user(request, f"{queryset.count()} task(s) reset — reminders will send again.")
reset_notification.short_description = "🔔 Reset notification (send reminder again)"

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'date', 'time', 'is_completed', 'is_notified']
    list_filter = ['is_completed', 'is_notified', 'date']
    search_fields = ['title', 'user__email']
    actions = [reset_notification]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']
