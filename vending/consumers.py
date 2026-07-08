import json
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction
from django.utils import timezone
from subscriptions.models import Subscription
from subscriptions.serializers import SubscriptionSerializer
from .models import DispenseLog, DispenseOrder, Machine
from .serializers import DispenseLogSerializer, DispenseOrderSerializer


@database_sync_to_async
def authorize_machine(serial, key):
    try:
        machine = Machine.objects.get(serial=serial)
    except Machine.DoesNotExist:
        return None
    if not machine.api_key or machine.api_key != key:
        return None
    machine.online = True
    machine.last_seen = timezone.now()
    machine.save(update_fields=['online', 'last_seen'])
    return {'serial': machine.serial, 'title': machine.title}


@database_sync_to_async
def mark_machine_offline(serial):
    Machine.objects.filter(serial=serial).update(online=False, last_seen=timezone.now())


@database_sync_to_async
def update_order_from_machine(message):
    order_id = message.get('order_id')
    event_type = message.get('type')
    if not order_id:
        return None

    try:
        actual_liters = Decimal(str(message.get('actual_liters', '0'))).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError):
        actual_liters = Decimal('0.00')

    with transaction.atomic():
        try:
            order = DispenseOrder.objects.select_for_update().select_related('subscription', 'machine', 'user').get(id=order_id)
        except DispenseOrder.DoesNotExist:
            return None

        subscription = None
        if order.subscription_id:
            subscription = Subscription.objects.select_for_update().select_related('plan').get(id=order.subscription_id)
        log = None

        if event_type == 'dispense.started':
            order.status = DispenseOrder.STATUS_DISPENSING
            order.started_at = order.started_at or timezone.now()
            order.save(update_fields=['status', 'started_at'])

        elif event_type == 'dispense.progress':
            order.status = DispenseOrder.STATUS_DISPENSING
            order.actual_liters = actual_liters
            order.started_at = order.started_at or timezone.now()
            order.save(update_fields=['status', 'actual_liters', 'started_at'])

        elif event_type == 'dispense.completed':
            if subscription and order.status != DispenseOrder.STATUS_COMPLETED:
                adjustment = actual_liters - order.requested_liters
                subscription.liters_used = max(subscription.liters_used + adjustment, Decimal('0.00'))
                subscription.save(update_fields=['liters_used'])

            order.status = DispenseOrder.STATUS_COMPLETED
            order.actual_liters = actual_liters
            order.completed_at = timezone.now()
            order.error_message = ''
            order.save(update_fields=['status', 'actual_liters', 'completed_at', 'error_message'])
            log, _ = DispenseLog.objects.get_or_create(
                order=order,
                defaults={
                    'subscription': subscription,
                    'machine': order.machine,
                    'liters': actual_liters,
                },
            )

        elif event_type == 'dispense.failed':
            if subscription and order.status not in [DispenseOrder.STATUS_FAILED, DispenseOrder.STATUS_CANCELLED, DispenseOrder.STATUS_COMPLETED]:
                subscription.liters_used = max(subscription.liters_used - order.requested_liters, Decimal('0.00'))
                subscription.save(update_fields=['liters_used'])
            order.status = DispenseOrder.STATUS_FAILED
            order.error_message = message.get('reason', 'machine_error')[:255]
            order.completed_at = timezone.now()
            order.save(update_fields=['status', 'error_message', 'completed_at'])

        order.refresh_from_db()
        if subscription:
            subscription.refresh_from_db()
        return {
            'user_id': order.user_id,
            'payload': {
                'type': 'dispense_order_update',
                'order': DispenseOrderSerializer(order).data,
                'subscription': SubscriptionSerializer(subscription).data if subscription else None,
                'log': DispenseLogSerializer(log).data if log else None,
            },
        }


class MachineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.serial = self.scope['url_route']['kwargs']['serial']
        query_string = self.scope.get('query_string', b'').decode()
        machine_key = parse_qs(query_string).get('machine_key', [None])[0]
        machine = await authorize_machine(self.serial, machine_key)
        if not machine:
            await self.close(code=4403)
            return

        self.group_name = f'machine_{self.serial}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'machine.connected',
            'machine': machine,
            'message': 'دستگاه به سرور وصل شد',
        }, ensure_ascii=False))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await mark_machine_offline(self.serial)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            message = json.loads(text_data or '{}')
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'type': 'error', 'detail': 'Invalid JSON'}))
            return

        event_type = message.get('type')
        if event_type in ['dispense.started', 'dispense.progress', 'dispense.completed', 'dispense.failed']:
            update = await update_order_from_machine(message)
            if update and update.get('user_id'):
                await self.channel_layer.group_send(
                    f"user_{update['user_id']}",
                    {'type': 'send_subscription_update', 'payload': update['payload']},
                )
            await self.send(text_data=json.dumps({'type': 'machine.ack', 'for': event_type}, ensure_ascii=False))
            return

        if event_type == 'machine.heartbeat':
            await authorize_machine(self.serial, parse_qs(self.scope.get('query_string', b'').decode()).get('machine_key', [None])[0])
            await self.send(text_data=json.dumps({'type': 'machine.heartbeat.ok'}, ensure_ascii=False))
            return

        await self.send(text_data=json.dumps({'type': 'machine.unknown_message'}, ensure_ascii=False))

    async def send_machine_command(self, event):
        await self.send(text_data=json.dumps(event['payload'], ensure_ascii=False))
