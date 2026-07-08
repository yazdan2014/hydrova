from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from vending.models import DispenseLog, DispenseOrder
from vending.serializers import DispenseLogSerializer, DispenseOrderSerializer
from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer


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
