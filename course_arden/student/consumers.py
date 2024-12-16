from venv import create
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
from channels.db import database_sync_to_async


from teacher.models import Feedback, Reply


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
        text_data_type = text_data_json["message_type"]
        user_id = text_data_json["user_id"]
        if text_data_type == "reply":
            feedback_id = text_data_json["feedback_id"]
            feedback_reply = await database_sync_to_async(Reply.objects.create)(
                content=message,
                user_id=user_id,
                feedback_id=feedback_id,
            )
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "feedback_reply",
                    "message": message,
                    "feedback_id": feedback_id,
                    "user_id": user_id,
                    "reply_id": feedback_reply.id,
                },
            )
        else:
            feedback = feedback = await database_sync_to_async(Feedback.objects.create)(
                content=message,
                user_id=user_id,
                course_id=self.course_id,
            )

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "feedback_message",
                    "message": message,
                    "feedback_id": feedback.id,
                    "user_id": user_id,
                },
            )

    async def feedback_message(self, event):
        message = event["message"]
        feedback_id = event["feedback_id"]
        user_id = event["user_id"]
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": "feedback",
                    "message": message,
                    "feedback_id": feedback_id,
                    "user_id": user_id,
                }
            )
        )

    async def feedback_reply(self, event):
        message = event["message"]
        feedback_id = event["feedback_id"]
        user_id = event["user_id"]
        reply_id = event["reply_id"]
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": "reply",
                    "message": message,
                    "feedback_id": feedback_id,
                    "user_id": user_id,
                    "reply_id": reply_id,
                }
            )
        )
