from django.contrib import admin
from .models import UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_dispense_liters', 'low_balance_alert_liters', 'updated_at')
    list_select_related = ('user',)
