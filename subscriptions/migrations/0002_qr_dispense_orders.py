# Generated for QR dispense flow.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='api_key',
            field=models.CharField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.CreateModel(
            name='QRSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('is_used', models.BooleanField(default=False)),
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qr_sessions', to='subscriptions.machine')),
            ],
        ),
        migrations.CreateModel(
            name='DispenseOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_liters', models.DecimalField(decimal_places=2, max_digits=6)),
                ('actual_liters', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('dispensing', 'Dispensing'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('error_message', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dispense_orders', to='subscriptions.machine')),
                ('qr_session', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='order', to='subscriptions.qrsession')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dispense_orders', to='subscriptions.subscription')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dispense_orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='dispenselog',
            name='order',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log', to='subscriptions.dispenseorder'),
        ),
    ]
