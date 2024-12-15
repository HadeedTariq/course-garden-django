from venv import create
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

from teacher.models import Feedback


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
        text_data_type  = text_data_json["message_type"]
        if text_data_type == 'reply':
            return "dfd"
        else:
            feedback=Feedback.objects.create(content=message,user_id='',course_id=self.course_id)
            feedback=feedback.save()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "feedback_message",
                    "message": message,
                    "feedback_id": feedback['id'],
                },
            )

    async def feedback_message(self, event):
        message = event["message"]
        feedback_id = event["feedback_id"]
        await self.send(text_data=json.dumps({"message": message,'feedback_id':feedback_id}))
