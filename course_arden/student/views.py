from django.http import JsonResponse
from django.shortcuts import redirect, render
from .utils import parse_price
from .decorators import course_middleware_decorator
from student.forms import CouponForm
import stripe
from django.conf import settings
from .serializers import CourseSerializer, PurchaseCourseSerializer
from teacher.models import CouponCode, Course, CourseEnrollement, CoursePurchasers
from django.views.decorators.csrf import csrf_exempt


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
    serializer = CourseSerializer(courses, many=True,context ={"user_id":(request.user_data and request.user_data['id']) or None})
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
                return redirect("student:pruchaseCourse", course_id)
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


@course_middleware_decorator
def purchase_course(request, course_id):
    user = request.user_data
    try:
        course = Course.objects.get(id=course_id)
        is_coupon_applied = course.coupons.filter(coupon_users__id=user["id"]).exists()
        currency, amount = parse_price(course.price)
        if is_coupon_applied:
            course.price = f"{currency} {amount / 2}"
        return render(
            request,
            "student/course_purchasing.html",
            {"course": course, "is_coupon_applied": is_coupon_applied},
        )
    except Exception as e:
        print(e)
        return JsonResponse({"message": "Course not found"}, status=404)


stripe.api_key = settings.STRIPE_SECRET_KEY
@csrf_exempt
@course_middleware_decorator
def checkout(request, course_id):
    user = request.user_data
    if request.method == "POST":
        try:
            course = Course.objects.get(id=course_id)
            is_coupon_applied = course.coupons.filter(
                coupon_users__id=user["id"]
            ).exists()
            currency, amount = parse_price(course.price)
            if is_coupon_applied:
                amount = amount // 2
            intent = stripe.PaymentIntent.create(
                amount=int(amount) * 100,
                currency="usd",
                metadata={"integration_check": "accept_a_payment"},
            )
            print(intent["client_secret"])
            if intent is not None:
                purchaser = CoursePurchasers.objects.create(
                    course_id=course,
                    student_id_id=user["id"],
                    price=f"{currency} {amount}",
                )
                enrollment = CourseEnrollement.objects.create(
                    student_id_id=user["id"],
                    course_id=course,
                )
                
                enrollment.save()
                purchaser.save()
                return JsonResponse({"clientSecret": intent["client_secret"]})
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=404)
    else:
        try:
            course = Course.objects.get(id=course_id)
            return render(
                request,
                "student/checkout.html",
                {"publishable_key": settings.STRIPE_PUBLIC_KEY, "course": course},
            )
        except Exception as e:
            print(e)
            return JsonResponse({"message": "Course not found"}, status=404)

@course_middleware_decorator
def myPurchasedCourses(request):
    purchases = CoursePurchasers.objects.filter(student_id_id=request.user_data["id"])
    try:
        serializer = PurchaseCourseSerializer(purchases,many=True)
        print(serializer.data)
        return JsonResponse({"courses":serializer.data},status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"message": "No purchases found"}, status=404)
    