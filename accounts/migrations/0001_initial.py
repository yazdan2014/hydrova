from decimal import Decimal
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_dispense_liters', models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=4)),
                ('low_balance_alert_liters', models.DecimalField(decimal_places=2, default=Decimal('10.00'), max_digits=5)),
                ('notify_low_balance', models.BooleanField(default=True)),
                ('notify_dispense_success', models.BooleanField(default=True)),
                ('notify_dispense_failed', models.BooleanField(default=True)),
                ('notify_machine_offline', models.BooleanField(default=False)),
                ('require_confirm_before_dispense', models.BooleanField(default=True)),
                ('security_alerts', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
