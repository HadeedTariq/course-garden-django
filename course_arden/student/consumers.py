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
        data = json.loads(text_data)
        message_type = data.get("message_type")

        # Dispatch to specific handler based on message type
        handler = getattr(self, f"handle_{message_type}", None)
        if handler:
            await handler(data)
        else:
            logger.warning(f"Unhandled message type: {message_type}")

    async def handle_feedback(self, data):
        message = data["message"]
        user_id = data["user_id"]

        feedback = await database_sync_to_async(Feedback.objects.create)(
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
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": "feedback",
                    "message": event["message"],
                    "feedback_id": event["feedback_id"],
                    "user_id": event["user_id"],
                }
            )
        )

    async def handle_reply(self, data):
        message = data["message"]
        user_id = data["user_id"]
        feedback_id = data["feedback_id"]

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

    async def feedback_reply(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": "reply",
                    "message": event["message"],
                    "feedback_id": event["feedback_id"],
                    "user_id": event["user_id"],
                    "reply_id": event["reply_id"],
                }
            )
        )

    async def handle_delete_feedback(self, data):
        feedback_id = data["feedback_id"]
        user_id = data["user_id"]
        await database_sync_to_async(
            Feedback.objects.filter(id=feedback_id, user_id=user_id).delete
        )()
        logger.info(f"Feedback {feedback_id} deleted by user {user_id}")

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "feedback_deleted",
                "feedback_id": feedback_id,
            },
        )

    async def feedback_deleted(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": "delete_feedback",
                    "feedback_id": event["feedback_id"],
                }
            )
        )

    async def handle_delete_reply(self, data):
        reply_id = data["reply_id"]
        user_id = data["user_id"]
        await database_sync_to_async(
            Reply.objects.filter(id=reply_id, user_id=user_id).delete
        )()
        logger.info(f"Reply {reply_id} deleted by user {user_id}")

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "reply_deleted",
                "reply_id": reply_id,
            },
        )

    async def reply_deleted(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message_type": "delete_reply",
                    "reply_id": event["reply_id"],
                }
            )
        )
