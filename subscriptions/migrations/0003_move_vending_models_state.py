from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_qr_dispense_orders'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='DispenseOrder'),
                migrations.DeleteModel(name='DispenseLog'),
                migrations.DeleteModel(name='QRSession'),
                migrations.DeleteModel(name='Machine'),
            ],
        ),
    ]
