import secrets
from django.conf import settings
from django.db import models
from django.utils import timezone


def make_machine_key():
    return secrets.token_urlsafe(32)


class Machine(models.Model):
    serial = models.CharField(max_length=80, unique=True)
    title = models.CharField(max_length=120)
    location = models.CharField(max_length=255, blank=True)
    online = models.BooleanField(default=False)
    filter_health_percent = models.PositiveSmallIntegerField(default=100)
    uv_status = models.CharField(max_length=40, default='active')
    last_seen = models.DateTimeField(null=True, blank=True)
    api_key = models.CharField(max_length=120, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = make_machine_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} ({self.serial})'

    class Meta:
        db_table = 'subscriptions_machine'


class QRSession(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='qr_sessions')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired

    def __str__(self):
        return f'QR {self.token[:8]} for {self.machine.serial}'

    class Meta:
        db_table = 'subscriptions_qrsession'


class DispenseOrder(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_DISPENSING = 'dispensing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_DISPENSING, 'Dispensing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dispense_orders', null=True, blank=True)
    subscription = models.ForeignKey('subscriptions.Subscription', on_delete=models.PROTECT, related_name='dispense_orders', null=True, blank=True)
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT, related_name='dispense_orders')
    qr_session = models.OneToOneField(QRSession, on_delete=models.PROTECT, related_name='order', null=True, blank=True)
    requested_liters = models.DecimalField(max_digits=6, decimal_places=2)
    actual_liters = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        owner = self.user.username if self.user else 'direct'
        return f'Order #{self.id} - {owner} - {self.requested_liters}L'

    class Meta:
        db_table = 'subscriptions_dispenseorder'


class DispenseLog(models.Model):
    subscription = models.ForeignKey('subscriptions.Subscription', on_delete=models.CASCADE, related_name='dispense_logs', null=True, blank=True)
    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL, null=True, blank=True, related_name='dispense_logs')
    liters = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.OneToOneField(DispenseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='log')

    def __str__(self):
        owner = self.subscription.user.username if self.subscription else 'direct'
        return f'{self.liters}L for {owner}'

    class Meta:
        db_table = 'subscriptions_dispenselog'
