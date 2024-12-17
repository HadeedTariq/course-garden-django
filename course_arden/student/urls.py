from django.urls import path
from . import views

app_name = "student"

urlpatterns = [
    path("get-courses/", views.getCourses, name="getCourses"),
    path("watch-course/<int:course_id>", views.watchCourse, name="watchCourse"),
    path("course/feedback/<int:course_id>", views.feedback, name="feedback"),
    path("enroll-in-course/", views.enrollInCourse, name="enrollInCourse"),
    path(
        "apply-coupon-code/<int:course_id>/",
        views.applyCouponCode,
        name="applyCouponCode",
    ),
    path(
        "course/purchase/<int:course_id>",
        views.purchase_course,
        name="pruchaseCourse",
    ),
    path(
        "course/checkout/purchase/<int:course_id>",
        views.checkout,
        name="courseCheckout",
    ),
    path(
        "myPurchasedCourses/",
        views.myPurchasedCourses,
        name="myPurchasedCourses",
    ),
    path(
        "myPoints/",
        views.getErolledCoursePoints,
        name="myPoints",
    ),
    path("playlists/<int:course_id>", views.playlist_handler, name="playlist_handler"),
]
