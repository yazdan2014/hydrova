from django.conf import settings
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    name = models.CharField(max_length=120)
    monthly_liters = models.PositiveIntegerField()
    price_toman = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} - {self.monthly_liters}L'


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='water_subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    month_start = models.DateField(default=timezone.localdate)
    liters_total = models.DecimalField(max_digits=8, decimal_places=2)
    liters_used = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def liters_remaining(self):
        return max(self.liters_total - self.liters_used, 0)

    def __str__(self):
        return f'{self.user.username} - {self.plan.name}'
