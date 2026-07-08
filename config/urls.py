from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import MeView, RegisterView, UserSettingsView
from subscriptions.views import (
    DashboardSummaryView,
    PlanViewSet,
    SubscriptionViewSet,
)
from vending.views import (
    ConfirmDispenseView,
    CreateQRSessionView,
    DirectDispenseView,
    MachineHeartbeatView,
    MachineViewSet,
    QRSessionDetailView,
    SimulateDispenseView,
)

router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plans')
router.register(r'machines', MachineViewSet, basename='machines')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscriptions')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/me/', MeView.as_view(), name='auth-me'),
    path('api/auth/settings/', UserSettingsView.as_view(), name='auth-settings'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('api/dashboard/simulate-dispense/', SimulateDispenseView.as_view(), name='simulate-dispense'),
    path('api/machines/<str:serial>/qr-session/', CreateQRSessionView.as_view(), name='machine-qr-session'),
    path('api/machines/<str:serial>/heartbeat/', MachineHeartbeatView.as_view(), name='machine-heartbeat'),
    path('api/machines/<str:serial>/direct-dispense/', DirectDispenseView.as_view(), name='machine-direct-dispense'),
    path('api/dispense/session/<str:token>/', QRSessionDetailView.as_view(), name='dispense-session'),
    path('api/dispense/session/<str:token>/confirm/', ConfirmDispenseView.as_view(), name='dispense-confirm'),
    path('api/', include(router.urls)),
]
