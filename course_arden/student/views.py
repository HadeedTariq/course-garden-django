from django.http import JsonResponse
from django.shortcuts import render

from teacher.models import Course


# Create your views here.
def get_courses(request):
    courses = Course.objects.filter().values()
    print(courses)
    return JsonResponse({"courses": courses}, status=200)
