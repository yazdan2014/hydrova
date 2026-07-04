from django.contrib import admin
from .models import DispenseLog, DispenseOrder, Machine, Plan, QRSession, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_liters', 'price_toman', 'is_active')


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('serial', 'title', 'location', 'online', 'filter_health_percent', 'uv_status', 'last_seen')
    readonly_fields = ('api_key',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'liters_total', 'liters_used', 'active', 'month_start')


@admin.register(QRSession)
class QRSessionAdmin(admin.ModelAdmin):
    list_display = ('machine', 'token_short', 'expires_at', 'is_used', 'used_at')
    readonly_fields = ('token', 'created_at')

    def token_short(self, obj):
        return obj.token[:12]


@admin.register(DispenseOrder)
class DispenseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'machine', 'requested_liters', 'actual_liters', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'machine')


@admin.register(DispenseLog)
class DispenseLogAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'machine', 'liters', 'created_at')
