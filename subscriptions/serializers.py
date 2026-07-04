from rest_framework import serializers
from .models import DispenseLog, Machine, Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'monthly_liters', 'price_toman', 'description']


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['id', 'serial', 'title', 'location', 'online', 'filter_health_percent', 'uv_status', 'last_seen']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    liters_remaining = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'month_start', 'liters_total', 'liters_used', 'liters_remaining', 'active', 'created_at']


class DispenseLogSerializer(serializers.ModelSerializer):
    machine = MachineSerializer(read_only=True)

    class Meta:
        model = DispenseLog
        fields = ['id', 'machine', 'liters', 'created_at']
