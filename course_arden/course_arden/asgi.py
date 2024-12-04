import os
from django.core.asgi import get_asgi_application
from django_tortoise import get_boosted_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "course_arden.settings")
application = get_asgi_application()
application = get_boosted_asgi_application(application)
