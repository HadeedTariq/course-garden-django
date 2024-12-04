from django.shortcuts import render, get_object_or_404, redirect

from .forms import CouponForm, CourseForm, ChapterForm
import cloudinary
from .models import Chapter, CouponCode, Course


# Create your views here.
def create_course(request):
    successmessage = ""
    errormessage = ""
    creator = getattr(request, "user_data", None)
    print(creator)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["thumbnail"]
            result = cloudinary.uploader.upload(file, upload_preset="ogypr3xk")
            thumbnail = result["secure_url"]
            title = request.POST.get("title")
            description = request.POST.get("description")
            price = request.POST.get("price")
            totalChapters = request.POST.get("totalChapters")
            category = request.POST.get("category")
            status = request.POST.get("status")
            course = Course.objects.create(
                title=title,
                description=description,
                price=price,
                totalChapters=totalChapters,
                category=category,
                status=status,
                thumbnail=thumbnail,
                creator=creator,
            )
            course.save()
            successmessage += "Course created successfully"
        else:
            errormessage += "Form is not valid"
    else:
        print(Course.objects.all().values())

        form = CourseForm()
    return render(
        request,
        "teacher/create_course.html",
        {"form": form, "successmessage": successmessage, "errormessage": errormessage},
    )


def create_coupon(request, course):
    successmessage = ""
    errormessage = ""
    if request.method == "POST":
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.course = course
            coupon.save()
        else:
            errormessage += "Form is not valid"


def publish_course(request, id):
    successmessage = ""
    errormessage = ""
    chapters_error = []
    course = get_object_or_404(Course, id=id)
    chapter_forms = [
        ChapterForm(prefix=f"form_{i}") for i in range(course.totalChapters)
    ]

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "coupon":
            coupon_form = CouponForm(request.POST)
            print(coupon_form)
            if coupon_form.is_valid():
                try:
                    coupon = coupon_form.save(commit=False)
                    coupon.course = course
                    coupon.save()
                    successmessage = "Coupon created successfully"
                except Exception as e:
                    errormessage = f"Error creating coupon: {e}"
            else:
                errormessage = "Coupon Form is not valid"
        elif form_type == "chapters":
            is_valid = True
            for i, form in enumerate(chapter_forms):
                thumbnail_file = request.FILES[f"form_{i}-thumbnail"]
                video_file = request.FILES[f"form_{i}-video"]

                # Upload the thumbnail image to Cloudinary
                thumbnail_result = cloudinary.uploader.upload(
                    thumbnail_file, upload_preset="ogypr3xk"
                )
                thumbnail_url = thumbnail_result["secure_url"]

                # Upload the video to Cloudinary
                video_result = cloudinary.uploader.upload(
                    video_file,
                    upload_preset="ogypr3xk",
                    resource_type="video",
                )
                video_url = video_result["secure_url"]

                title = request.POST.get(f"form_{i}-title")
                description = request.POST.get(f"form_{i}-description")
                chapter_number = request.POST.get(f"form_{i}-chapter_number")

                chapter = Chapter.objects.create(
                    title=title,
                    description=description,
                    thumbnail=thumbnail_url,
                    chapter_number=chapter_number,
                    video=video_url,
                    course=course,
                )
                chapter.save()
            if is_valid:
                successmessage = "Chapters successfully"

    couponForm = CouponForm()

    return render(
        request,
        "teacher/publish_course.html",
        {
            "chapter_forms": chapter_forms,
            "couponForm": couponForm,
            "course": course,
            "successmessage": successmessage,
            "errormessage": errormessage,
            "chapters_error": chapters_error,
        },
    )
