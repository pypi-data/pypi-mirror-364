# login_activity/admin.py
from django.contrib import admin
from .models import LoginActivity


@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'timestamp')
    search_fields = ('user__username', 'ip_address')
    list_filter = ('timestamp',)
