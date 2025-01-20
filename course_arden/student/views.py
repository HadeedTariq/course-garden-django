from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.db.models import Sum

from .tasks import sendEmailOnCoursePurchase

from .models import PlayList, Playlist_Course
from .utils import parse_price
from .decorators import course_middleware_decorator
from student.forms import CouponForm
import stripe
from django.conf import settings
from .serializers import (
    CourseSerializer,
    FeedbackSerializer,
    PlaylistSerializer,
    PurchaseCourseSerializer,
)
from teacher.models import (
    CouponCode,
    Course,
    CourseEnrollement,
    CoursePurchasers,
    Feedback,
)
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def getCourses(request):
    CoursePurchasers.objects.all().delete()
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
    serializer = CourseSerializer(
        courses,
        many=True,
        context={"user_id": (request.user_data and request.user_data["id"]) or None},
    )
    courses_data = serializer.data

    return render(request, "student/all_courses.html", {"courses": courses_data})


@course_middleware_decorator
def watchCourse(request, course_id):
    try:
        course = Course.objects.filter(id=course_id).first()
        return render(request, "student/watch-course.html", {"course": course})
    except Exception as e:
        return JsonResponse({"message": "Course not found."}, status=404)


@course_middleware_decorator
def feedback(request, course_id):
    user_data = request.user_data

    try:
        course = Course.objects.filter(id=course_id).first()
        if not course:
            return JsonResponse({"message": "Course not found."}, status=404)
        feedbacks = (
            Feedback.objects.filter(course=course)
            .select_related("user")
            .prefetch_related("replies")
        )
        feedback_serializer = FeedbackSerializer(
            feedbacks,
            many=True,
        )
        return render(
            request,
            "student/feedback.html",
            {
                "course": course,
                "course_id": course_id,
                "user": user_data,
                "feedbacks": feedback_serializer.data,
            },
        )
    except Exception as e:
        print(e)
        return JsonResponse({"message": "Something went wrong"}, status=404)


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
                sendEmailOnCoursePurchase.delay(user["id"])

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
        serializer = PurchaseCourseSerializer(purchases, many=True)
        print(serializer.data)
        return JsonResponse({"courses": serializer.data}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"message": "No purchases found"}, status=404)


@course_middleware_decorator
def getErolledCoursePoints(request):
    try:
        courses_points = CourseEnrollement.objects.filter(
            student_id_id=request.user_data["id"]
        ).aggregate(total_points=Sum("points"))
        return JsonResponse({"coursesPoints": courses_points}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"message": "No purchases found"}, status=404)


@course_middleware_decorator
def playlist_handler(request, course_id):
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return JsonResponse({"message": "Course not found."}, status=404)

    user_id = request.user_data["id"]

    playlists = PlayList.objects.filter(user_id=user_id).all()
    playlist_serializer = PlaylistSerializer(
        playlists,
        many=True,
        context={"course_id": course_id},
    )

    # Initialize message variables
    success_message = None
    error_message = None
    method = request.POST.get("_method")

    if method == "POST":
        title = request.POST.get("title")
        playlist_type = request.POST.get("type")

        try:
            playlist = PlayList.objects.create(
                title=title, user_id=user_id, type=playlist_type
            )
            playlist.save()
            success_message = "Playlist created successfully."

        except IntegrityError:
            error_message = "A playlist with this title already exists for this user."
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"

    if method == "UPDATEPLAYLISTPOST":
        last_title = request.POST.get("last_title")
        print(last_title)
        title = request.POST.get("title")

        playlist_type = request.POST.get("type")

        try:
            playlist = PlayList.objects.get(title=last_title, user_id=user_id)
            playlist.title = title
            playlist.type = playlist_type
            playlist.save()
            success_message = "Playlist updated successfully."

        except IntegrityError as error:
            print(error)

            error_message = "A playlist with this title already exists for this user."
        except Exception as e:
            print(e)
            error_message = f"An unexpected error occurred: {str(e)}"

    if method == "PUT":

        playlist_id = request.POST.get("playlist_id")
        try:
            playlist = PlayList.objects.get(id=playlist_id, user_id=user_id)
            Playlist_Course.objects.create(playlist=playlist, course=course)
            success_message = "Course added to playlist successfully."

        except IntegrityError:
            error_message = "Course already added to playlist"
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"

    if method == "DELETE":

        playlist_id = request.POST.get("playlist_id")
        try:
            PlayList.objects.filter(id=playlist_id, user_id=user_id).delete()
            success_message = "Playlist deleted successfully"

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"

    if method == "UPDATEPLAYLIST":
        playlist_value = request.POST.get("playlist_value")
        playlist_type = request.POST.get("playlist_type")
        return render(
            request,
            "student/playlist.html",
            {
                "playlists": playlist_serializer.data,
                "success_message": success_message,
                "error_message": error_message,
                "playlist_value": playlist_value,
                "playlist_type": playlist_type,
            },
        )

    return render(
        request,
        "student/playlist.html",
        {
            "playlists": playlist_serializer.data,
            "success_message": success_message,
            "error_message": error_message,
            "playlist_value": "",
        },
    )
