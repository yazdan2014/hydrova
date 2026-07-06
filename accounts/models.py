from decimal import Decimal
from django.conf import settings
from django.db import models


class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    default_dispense_liters = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.00'))
    low_balance_alert_liters = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    notify_low_balance = models.BooleanField(default=True)
    notify_dispense_success = models.BooleanField(default=True)
    notify_dispense_failed = models.BooleanField(default=True)
    notify_machine_offline = models.BooleanField(default=False)
    require_confirm_before_dispense = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Settings for {self.user.username}'
