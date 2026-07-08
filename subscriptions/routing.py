from django.urls import path
from .consumers import SubscriptionConsumer

websocket_urlpatterns = [
    path('ws/subscriptions/', SubscriptionConsumer.as_asgi()),
]
