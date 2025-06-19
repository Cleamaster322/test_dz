import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BooksConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("books", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("books", self.channel_name)

    async def receive(self, text_data):
        pass

    async def book_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'book_update',
            'action': event['action'],
            'book_id': event['book_id']
        }))