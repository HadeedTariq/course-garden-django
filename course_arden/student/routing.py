from django.urls import path

from .consumers import FeedbackConsumer


websocket_urlpatterns = [
    path("ws/feedback/<int:course_id>", FeedbackConsumer.as_asgi()),
]
