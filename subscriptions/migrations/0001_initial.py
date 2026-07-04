# Generated starter migration for the water vending platform.

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial', models.CharField(max_length=80, unique=True)),
                ('title', models.CharField(max_length=120)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('online', models.BooleanField(default=False)),
                ('filter_health_percent', models.PositiveSmallIntegerField(default=100)),
                ('uv_status', models.CharField(default='active', max_length=40)),
                ('last_seen', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('monthly_liters', models.PositiveIntegerField()),
                ('price_toman', models.PositiveIntegerField()),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month_start', models.DateField(default=django.utils.timezone.localdate)),
                ('liters_total', models.DecimalField(decimal_places=2, max_digits=8)),
                ('liters_used', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='subscriptions.plan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='water_subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DispenseLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liters', models.DecimalField(decimal_places=2, max_digits=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dispense_logs', to='subscriptions.machine')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dispense_logs', to='subscriptions.subscription')),
            ],
        ),
    ]
