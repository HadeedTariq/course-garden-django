from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("register/", views.registerUser, name="registerUser"),
    path("verify/", views.verifyUser, name="verifyUser"),
    path("login/", views.loginUser, name="loginUser"),
    path("profile/", views.getUser, name="getUser"),
    path("logout/", views.logout_user, name="logoutUser"),
    path("register_google/", views.register_google, name="registerGoogle"),
]
