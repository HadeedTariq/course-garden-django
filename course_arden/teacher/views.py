from django.shortcuts import render
from .forms import CourseForm
import cloudinary
from .models import Course


# Create your views here.
def create_course(request):
    successmessage = ""
    errormessage = ""
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
            )
            course.save()
            successmessage += "Course created successfully"
        else:
            errormessage += "Form is not valid"
    else:

        form = CourseForm()
    return render(
        request,
        "teacher/create_course.html",
        {"form": form, "successmessage": successmessage, "errormessage": errormessage},
    )


def publish_course(request, id):
    successmessage = ""
    errormessage = ""
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
            )
            course.save()
            successmessage += "Course created successfully"
        else:
            errormessage += "Form is not valid"
    else:

        form = CourseForm()
    return render(
        request,
        "teacher/publish_course.html",
        {"form": form, "successmessage": successmessage, "errormessage": errormessage},
    )
