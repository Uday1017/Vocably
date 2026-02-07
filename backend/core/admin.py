from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Analysis

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'is_staff', 'created_at']
    search_fields = ['email', 'username']

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'filename', 'status', 'overall_score', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'filename']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
