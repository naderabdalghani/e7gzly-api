import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ReservationsConsumer(WebsocketConsumer):

    def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        async_to_sync(self.channel_layer.group_add)(
            self.match_id,
            self.channel_name
        )
        self.accept()

    def update(self, event):
        self.send(text_data=json.dumps({'seat_id': event["seat_id"]}))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.match_id,
            self.channel_name
        )
