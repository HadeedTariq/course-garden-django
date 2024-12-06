from django.urls import path
from . import views

app_name = "student"

urlpatterns = [
    path("get-courses/", views.get_courses, name="getCourses"),
]
