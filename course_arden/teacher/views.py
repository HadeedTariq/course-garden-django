from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .forms import CouponForm, CourseForm, ChapterForm
import cloudinary
from .models import Chapter, Course
from djmoney.money import Money  # This is the proper Money class to use


# Create your views here.
def create_course(request):
    successmessage = ""
    errormessage = ""
    creator = getattr(request, "user_data", None)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            price = request.POST.get("price_0")
            currency = request.POST.get("price_1")
            actual_price = Money(price, currency)
            status = request.POST.get("status")

            is_valid_course = Course.price_validation(actual_price, status)

            if is_valid_course["error"] != None:
                errormessage += "Course price is required"

            else:
                file = request.FILES["thumbnail"]
                result = cloudinary.uploader.upload(file, upload_preset="ogypr3xk")
                thumbnail = result["secure_url"]
                title = request.POST.get("title")
                description = request.POST.get("description")
                totalChapters = request.POST.get("totalChapters")
                category = request.POST.get("category")

                course = Course.objects.create(
                    title=title,
                    description=description,
                    price=str(actual_price),
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
                try:
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
                except Exception as e:
                    print(e)
                    is_valid = False
                    errormessage = "Error creating chapter"
            if is_valid:
                successmessage = "Chapters created successfully"
        elif form_type == "publish":
            course.is_publish = True
            course.save()
            successmessage = "Coupon published successfully"

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


def my_courses(request):

    courses = Course.objects.filter(creator=request.user_data.id)

    results = []
    for course in courses:
        chapters = Chapter.objects.filter(course_id=course.id)
        results.append(
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "thumbnail": course.thumbnail,
                "totalChapters": course.totalChapters,
                "totalChapters": course.totalChapters,
                "status": course.status,
                "price": course.price,
                "category": course.category,
                "chapters": [
                    {
                        "id": chapter.id,
                        "title": chapter.title,
                        "description": chapter.description,
                        "thumbnail": chapter.thumbnail,
                        "video": chapter.video,
                        "chapter_number": chapter.chapter_number,
                    }
                    for chapter in chapters
                ],
            }
        )
    print(results)
    return JsonResponse({"results": results}, status=200)
