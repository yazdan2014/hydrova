from django.contrib import admin
from .models import DispenseLog, Machine, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_liters', 'price_toman', 'is_active')


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('serial', 'title', 'location', 'online', 'filter_health_percent', 'uv_status', 'last_seen')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'liters_total', 'liters_used', 'active', 'month_start')


@admin.register(DispenseLog)
class DispenseLogAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'machine', 'liters', 'created_at')
