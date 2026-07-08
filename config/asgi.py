import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from subscriptions.middleware import JWTAuthMiddleware
from subscriptions.routing import websocket_urlpatterns as subscription_websocket_urlpatterns
from vending.routing import websocket_urlpatterns as vending_websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': JWTAuthMiddleware(URLRouter(subscription_websocket_urlpatterns + vending_websocket_urlpatterns)),
})
