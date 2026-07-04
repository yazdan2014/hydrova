from django.urls import path
from .consumers import MachineConsumer, SubscriptionConsumer

websocket_urlpatterns = [
    path('ws/subscriptions/', SubscriptionConsumer.as_asgi()),
    path('ws/machines/<str:serial>/', MachineConsumer.as_asgi()),
]
