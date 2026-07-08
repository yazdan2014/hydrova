from rest_framework import serializers
from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'monthly_liters', 'price_toman', 'description']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    liters_remaining = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'month_start', 'liters_total', 'liters_used', 'liters_remaining', 'active', 'created_at']
