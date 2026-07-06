import secrets
from decimal import Decimal, InvalidOperation
from datetime import timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DispenseLog, DispenseOrder, Machine, Plan, QRSession, Subscription
from .serializers import (
    DispenseLogSerializer,
    DispenseOrderSerializer,
    MachineSerializer,
    PlanSerializer,
    QRSessionSerializer,
    SubscriptionSerializer,
)


ALLOWED_DISPENSE_LITERS = [Decimal('0.50'), Decimal('1.00'), Decimal('1.50'), Decimal('2.00')]


def decimal_from_request(value, default='1.00'):
    try:
        return Decimal(str(value if value is not None else default)).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError):
        return None


def frontend_base_url():
    return getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')


def machine_is_authorized(request, machine):
    supplied_key = request.headers.get('X-Machine-Key') or request.data.get('machine_key')
    return bool(machine.api_key and supplied_key and secrets.compare_digest(machine.api_key, supplied_key))


def send_to_user(user_id, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {'type': 'send_subscription_update', 'payload': payload},
    )


def send_to_machine(serial, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'machine_{serial}',
        {'type': 'send_machine_command', 'payload': payload},
    )


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.filter(is_active=True).order_by('monthly_liters')
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class MachineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Machine.objects.all().order_by('serial')
    serializer_class = MachineSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).select_related('plan').order_by('-created_at')

    @action(detail=False, methods=['get'])
    def my(self, request):
        subscription = self.get_queryset().filter(active=True).first()
        if not subscription:
            return Response({'detail': 'No active subscription found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(subscription).data)


class DashboardSummaryView(APIView):
    def get(self, request):
        subscription = Subscription.objects.filter(user=request.user, active=True).select_related('plan').first()
        recent_logs = DispenseLog.objects.filter(subscription__user=request.user).select_related('machine', 'order').order_by('-created_at')[:8]
        open_orders = DispenseOrder.objects.filter(
            user=request.user,
            status__in=[DispenseOrder.STATUS_PENDING, DispenseOrder.STATUS_SENT, DispenseOrder.STATUS_DISPENSING],
        ).select_related('machine').order_by('-created_at')[:5]
        return Response({
            'subscription': SubscriptionSerializer(subscription).data if subscription else None,
            'recent_logs': DispenseLogSerializer(recent_logs, many=True).data,
            'open_orders': DispenseOrderSerializer(open_orders, many=True).data,
        })


class SimulateDispenseView(APIView):
    def post(self, request):
        liters = decimal_from_request(request.data.get('liters'), '1.00')
        serial = request.data.get('machine_serial', 'DEMO-001')
        if liters is None or liters <= 0:
            return Response({'detail': 'Liters must be positive.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            subscription = Subscription.objects.select_for_update().filter(user=request.user, active=True).first()
            if not subscription:
                return Response({'detail': 'No active subscription found.'}, status=status.HTTP_404_NOT_FOUND)
            if subscription.liters_remaining < liters:
                return Response({'detail': 'Not enough liters left.'}, status=status.HTTP_400_BAD_REQUEST)

            machine, _ = Machine.objects.get_or_create(
                serial=serial,
                defaults={'title': 'دستگاه آزمایشی', 'location': 'لابی ساختمان', 'online': True},
            )
            subscription.liters_used += liters
            subscription.save(update_fields=['liters_used'])
            log = DispenseLog.objects.create(subscription=subscription, machine=machine, liters=liters)

        payload = {
            'type': 'subscription_update',
            'subscription': SubscriptionSerializer(subscription).data,
            'log': DispenseLogSerializer(log).data,
        }
        send_to_user(request.user.id, payload)
        return Response(payload)


class CreateQRSessionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, serial):
        try:
            machine = Machine.objects.get(serial=serial)
        except Machine.DoesNotExist:
            return Response({'detail': 'Machine not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not machine_is_authorized(request, machine):
            return Response({'detail': 'Machine key is invalid.'}, status=status.HTTP_403_FORBIDDEN)

        now = timezone.now()
        machine.online = True
        machine.last_seen = now
        machine.save(update_fields=['online', 'last_seen'])

        QRSession.objects.filter(machine=machine, is_used=False, expires_at__lt=now).update(is_used=True, used_at=now)
        token = secrets.token_urlsafe(32)
        session = QRSession.objects.create(
            machine=machine,
            token=token,
            expires_at=now + timedelta(seconds=90),
        )
        qr_url = f'{frontend_base_url()}/dashboard/dispense/{session.token}'
        return Response({
            'session': QRSessionSerializer(session).data,
            'qr_url': qr_url,
            'expires_in_seconds': 90,
        }, status=status.HTTP_201_CREATED)


class MachineHeartbeatView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, serial):
        try:
            machine = Machine.objects.get(serial=serial)
        except Machine.DoesNotExist:
            return Response({'detail': 'Machine not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not machine_is_authorized(request, machine):
            return Response({'detail': 'Machine key is invalid.'}, status=status.HTTP_403_FORBIDDEN)

        machine.online = True
        machine.last_seen = timezone.now()
        machine.save(update_fields=['online', 'last_seen'])
        return Response({'detail': 'ok', 'machine': MachineSerializer(machine).data})


class QRSessionDetailView(APIView):
    def get(self, request, token):
        try:
            session = QRSession.objects.select_related('machine').get(token=token)
        except QRSession.DoesNotExist:
            return Response({'detail': 'QR session not found.'}, status=status.HTTP_404_NOT_FOUND)

        subscription = Subscription.objects.filter(user=request.user, active=True).select_related('plan').first()
        active_order = getattr(session, 'order', None)
        return Response({
            'session': QRSessionSerializer(session).data,
            'subscription': SubscriptionSerializer(subscription).data if subscription else None,
            'order': DispenseOrderSerializer(active_order).data if active_order else None,
        })


class ConfirmDispenseView(APIView):
    def post(self, request, token):
        liters = decimal_from_request(request.data.get('liters'), '1.00')
        if liters is None or liters <= 0:
            return Response({'detail': 'Liters must be positive.'}, status=status.HTTP_400_BAD_REQUEST)
        if liters not in ALLOWED_DISPENSE_LITERS:
            return Response({'detail': 'This dispense amount is not allowed yet.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            try:
                session = QRSession.objects.select_for_update().select_related('machine').get(token=token)
            except QRSession.DoesNotExist:
                return Response({'detail': 'QR session not found.'}, status=status.HTTP_404_NOT_FOUND)

            if session.is_used:
                return Response({'detail': 'This QR was already used.'}, status=status.HTTP_400_BAD_REQUEST)
            if session.is_expired:
                return Response({'detail': 'This QR has expired. Please scan the new QR on the machine.'}, status=status.HTTP_400_BAD_REQUEST)

            subscription = Subscription.objects.select_for_update().filter(user=request.user, active=True).select_related('plan').first()
            if not subscription:
                return Response({'detail': 'No active subscription found.'}, status=status.HTTP_404_NOT_FOUND)
            if subscription.liters_remaining < liters:
                return Response({'detail': 'Not enough liters left.'}, status=status.HTTP_400_BAD_REQUEST)

            session.is_used = True
            session.used_at = timezone.now()
            session.save(update_fields=['is_used', 'used_at'])

            subscription.liters_used += liters
            subscription.save(update_fields=['liters_used'])

            order = DispenseOrder.objects.create(
                user=request.user,
                subscription=subscription,
                machine=session.machine,
                qr_session=session,
                requested_liters=liters,
                status=DispenseOrder.STATUS_SENT,
            )

        order_payload = DispenseOrderSerializer(order).data
        subscription_payload = SubscriptionSerializer(subscription).data
        command = {
            'type': 'dispense.start',
            'order': order_payload,
            'order_id': order.id,
            'liters': str(liters),
            'max_duration_seconds': 30,
        }
        send_to_machine(order.machine.serial, command)
        send_to_user(order.user_id, {
            'type': 'dispense_order_update',
            'order': order_payload,
            'subscription': subscription_payload,
            'log': None,
        })
        return Response({
            'detail': 'Dispense command sent.',
            'order': order_payload,
            'subscription': subscription_payload,
        }, status=status.HTTP_201_CREATED)
