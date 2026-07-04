from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.models import Machine, Plan, Subscription


class Command(BaseCommand):
    help = 'Create demo plans, a demo user, a demo subscription, and a demo machine.'

    def handle(self, *args, **options):
        plans = [
            ('قطره', 60, 180000, 'برای مصرف سبک ماهانه و خانواده‌های کم‌مصرف'),
            ('چشمه', 150, 390000, 'انتخاب محبوب برای خانه و دفتر کوچک'),
            ('آبشار', 300, 690000, 'برای خانواده پرمصرف یا محیط کاری'),
        ]
        created_plans = []
        for name, liters, price, desc in plans:
            plan, _ = Plan.objects.get_or_create(
                name=name,
                defaults={'monthly_liters': liters, 'price_toman': price, 'description': desc},
            )
            created_plans.append(plan)

        user, created = User.objects.get_or_create(username='demo', defaults={'email': 'demo@example.com', 'first_name': 'کاربر'})
        if created:
            user.set_password('demo12345')
            user.save()

        Machine.objects.get_or_create(
            serial='DEMO-001',
            defaults={'title': 'آب‌ساز هوشمند شماره ۱', 'location': 'لابی ساختمان', 'online': True, 'last_seen': timezone.now()},
        )

        Subscription.objects.get_or_create(
            user=user,
            active=True,
            defaults={'plan': created_plans[1], 'liters_total': created_plans[1].monthly_liters, 'liters_used': 24},
        )

        self.stdout.write(self.style.SUCCESS('Demo data is ready. username=demo password=demo12345'))
