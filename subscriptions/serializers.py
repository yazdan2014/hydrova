from rest_framework import serializers
from .models import DispenseLog, DispenseOrder, Machine, Plan, QRSession, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'monthly_liters', 'price_toman', 'description']


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['id', 'serial', 'title', 'location', 'online', 'filter_health_percent', 'uv_status', 'last_seen']


class MachinePrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['id', 'serial', 'title', 'location', 'online', 'filter_health_percent', 'uv_status', 'last_seen', 'api_key']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    liters_remaining = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'month_start', 'liters_total', 'liters_used', 'liters_remaining', 'active', 'created_at']


class QRSessionSerializer(serializers.ModelSerializer):
    machine = MachineSerializer(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = QRSession
        fields = ['id', 'machine', 'token', 'created_at', 'expires_at', 'is_used', 'is_expired', 'is_valid']


class DispenseOrderSerializer(serializers.ModelSerializer):
    machine = MachineSerializer(read_only=True)

    class Meta:
        model = DispenseOrder
        fields = [
            'id', 'machine', 'requested_liters', 'actual_liters', 'status',
            'error_message', 'created_at', 'started_at', 'completed_at'
        ]


class DispenseLogSerializer(serializers.ModelSerializer):
    machine = MachineSerializer(read_only=True)
    order = DispenseOrderSerializer(read_only=True)

    class Meta:
        model = DispenseLog
        fields = ['id', 'machine', 'liters', 'created_at', 'order']
