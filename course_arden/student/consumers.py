from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



logger = logging.getLogger("django")


class FeedbackConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"WebSocket connection from {self.scope['client']}")
        await self.channel_layer.group_add("broadcast", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.channel_layer.group_send(
                "broadcast",
                {
                    "type": "broadcast_message",  # This maps to the broadcast_message function below
                    "message": message,
                }
            )
    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))

        


        
