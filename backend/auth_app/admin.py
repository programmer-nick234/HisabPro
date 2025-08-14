from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'phone', 'gst_number', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'company_name']
    readonly_fields = ['created_at', 'updated_at']
