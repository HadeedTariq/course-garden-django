from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging


logger = logging.getLogger("django")


class FeedbackConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        logger.info(f"WebSocket connection from {self.scope['client']}")
        self.course_id = self.scope["url_route"]["kwargs"]["course_id"]
        self.group_name = f"course_{self.course_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "feedback_message",
                "message": message,
            },
        )

    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
