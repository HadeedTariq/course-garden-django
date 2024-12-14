from channels.generic.websocket import WebsocketConsumer
import json
import logging

logger = logging.getLogger("django")


class FeedbackConsumer(WebsocketConsumer):
    def connect(self):
        logger.info(f"WebSocket connection from {self.scope['client']}")
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        self.channel_layer.group_send(
            text_data=json.dumps({"message": text_data_json["message"]})
        )
