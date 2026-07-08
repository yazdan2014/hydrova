import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SubscriptionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or self.user.is_anonymous:
            await self.close(code=4401)
            return

        self.group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': 'اتصال زنده داشبورد برقرار شد',
        }, ensure_ascii=False))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        await self.send(text_data=json.dumps({'type': 'pong'}, ensure_ascii=False))

    async def send_subscription_update(self, event):
        await self.send(text_data=json.dumps(event['payload'], ensure_ascii=False))
