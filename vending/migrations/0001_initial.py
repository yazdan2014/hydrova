import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscriptions', '0003_move_vending_models_state'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
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
                        ('api_key', models.CharField(blank=True, max_length=120, null=True, unique=True)),
                    ],
                    options={'db_table': 'subscriptions_machine'},
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
                        ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qr_sessions', to='vending.machine')),
                    ],
                    options={'db_table': 'subscriptions_qrsession'},
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
                        ('machine', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dispense_orders', to='vending.machine')),
                        ('qr_session', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='order', to='vending.qrsession')),
                        ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dispense_orders', to='subscriptions.subscription')),
                        ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dispense_orders', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={'db_table': 'subscriptions_dispenseorder'},
                ),
                migrations.CreateModel(
                    name='DispenseLog',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('liters', models.DecimalField(decimal_places=2, max_digits=6)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dispense_logs', to='vending.machine')),
                        ('order', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log', to='vending.dispenseorder')),
                        ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dispense_logs', to='subscriptions.subscription')),
                    ],
                    options={'db_table': 'subscriptions_dispenselog'},
                ),
            ],
        ),
    ]
