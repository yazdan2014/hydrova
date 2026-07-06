from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserSettings


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar_url']

    def get_avatar_url(self, obj):
        return ''


class UserSettingsSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True, max_length=150)
    email = serializers.EmailField(source='user.email', required=False, allow_blank=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserSettings
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'default_dispense_liters',
            'low_balance_alert_liters',
            'notify_low_balance',
            'notify_dispense_success',
            'notify_dispense_failed',
            'notify_machine_offline',
            'require_confirm_before_dispense',
            'security_alerts',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['username', 'created_at', 'updated_at']

    def validate_default_dispense_liters(self, value):
        allowed = {'0.50', '1.00', '1.50', '2.00'}
        if f'{value:.2f}' not in allowed:
            raise serializers.ValidationError('Default dispense amount must be one of 0.50, 1.00, 1.50, or 2.00 liters.')
        return value

    def validate_low_balance_alert_liters(self, value):
        if value < 0:
            raise serializers.ValidationError('Low balance alert must be zero or more.')
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for field, value in user_data.items():
            setattr(user, field, value)
        if user_data:
            user.save(update_fields=list(user_data.keys()))
        return super().update(instance, validated_data)
