from django.urls import path
from . import views

app_name = "student"

urlpatterns = [
    path("get-courses/", views.getCourses, name="getCourses"),
    path("enroll-in-course/", views.enrollInCourse, name="enrollInCourse"),
    path("apply-coupon-code/<int:course_id>/", views.applyCouponCode, name="appyCouponCode"),
]
