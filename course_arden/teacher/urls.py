from django.urls import path
from . import views

app_name = "teacher"

urlpatterns = [
    path("create-course/", views.create_course, name="createCourse"),
    path("create-course/<int:id>/", views.publish_course, name="publishCourse"),
    path("my-courses/", views.my_courses, name="myCourses"),
    # path("verify/", views.verifyUser, name="verifyUser"),
    # path("login/", views.loginUser, name="loginUser"),
    # path("profile/", views.getUser, name="getUser"),
    # path("logout/", views.logout_user, name="logoutUser"),
    # path("register_google/", views.register_google, name="registerGoogle"),
]
