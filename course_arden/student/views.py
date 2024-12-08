from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render

from .serializers import CourseSerializer
from teacher.models import Course, CourseEnrollement


# Create your views here.
def get_courses(request):
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


def enrollInCourse(request):
    if request.validation_err != "":
        return JsonResponse({"message": request.validation_err}, status=400)
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
