from decimal import Decimal
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DispenseLog, Machine, Plan, Subscription
from .serializers import DispenseLogSerializer, PlanSerializer, SubscriptionSerializer


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.filter(is_active=True).order_by('monthly_liters')
    serializer_class = PlanSerializer
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
        recent_logs = DispenseLog.objects.filter(subscription__user=request.user).select_related('machine').order_by('-created_at')[:8]
        return Response({
            'subscription': SubscriptionSerializer(subscription).data if subscription else None,
            'recent_logs': DispenseLogSerializer(recent_logs, many=True).data,
        })


class SimulateDispenseView(APIView):
    def post(self, request):
        liters = Decimal(str(request.data.get('liters', '1')))
        serial = request.data.get('machine_serial', 'DEMO-001')
        if liters <= 0:
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
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f'user_{request.user.id}', {'type': 'send_subscription_update', 'payload': payload})
        return Response(payload)
