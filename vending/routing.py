from django.urls import path
from .consumers import MachineConsumer


websocket_urlpatterns = [
    path('ws/machines/<str:serial>/', MachineConsumer.as_asgi()),
]
