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
        data = json.loads(text_data)
        self.send(text_data=json.dumps({'message': 'Feedback received!'}))
