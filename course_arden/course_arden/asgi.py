import os
from django.core.asgi import get_asgi_application
from django_tortoise import get_boosted_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from student.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "course_arden.settings")
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
