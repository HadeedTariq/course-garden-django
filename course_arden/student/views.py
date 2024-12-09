from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render

from authentication.models import User
from .decorators import course_middleware_decorator
from student.forms import CouponForm

from .serializers import CourseSerializer
from teacher.models import CouponCode, Course, CourseEnrollement


# Create your views here.
def getCourses(request):
    if request.user_data:
        courses = (
            Course.objects.filter(is_publish=True)
            .exclude(creator=request.user_data["id"])
            .select_related("creator")
            .prefetch_related("chapters")
        )
    else:
        courses = (
            Course.objects.filter(is_publish=True)
            .select_related("creator")
            .prefetch_related("chapters")
        )
    serializer = CourseSerializer(courses, many=True)
    courses_data = serializer.data
    return render(request, "student/all_courses.html", {"courses": courses_data})


@course_middleware_decorator
def enrollInCourse(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        user_id = request.user_data["id"]
        if course_id and user_id:
            course = Course.objects.get(id=course_id)
            if course.status != "paid":
                course_enrollement = CourseEnrollement.objects.create(
                    student_id=user_id, course_id=course_id
                )
                course_enrollement.save()
                return JsonResponse(
                    {"message": "Course enrolled successfully."}, status=200
                )
            else:
                return JsonResponse({"message": "This course is not free."}, status=400)
        else:
            return JsonResponse(
                {"message": "Missing course_id or user_id."}, status=400
            )
    else:
        return JsonResponse({"message": "Invalid request method."}, status=405)


@course_middleware_decorator
def applyCouponCode(request, course_id):
    successmessage = ""
    errormessage = ""
    if request.method == "POST":
        coupon = request.POST.get("coupon")
        try:
            actual_coupon = CouponCode.objects.get(
                coupon=coupon, course=course_id, quantity__gt=0
            )
            errormessage = ""
            if actual_coupon:
                actual_coupon.coupon_users.add(request.user_data["id"])
                actual_coupon.quantity = actual_coupon.quantity - 1
                actual_coupon.save()
                successmessage = "Coupon code applied successfully."
        except Exception as e:
            errormessage = "Invalid coupon code or coupon not available."
    form = CouponForm()
    return render(
        request,
        "student/apply_coupon_code.html",
        {"form": form, "successmessage": successmessage, "errormessage": errormessage},
    )
