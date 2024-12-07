from django.db import connection
from django.http import JsonResponse

from .serializers import CourseSerializer
from teacher.models import Course


# Create your views here.
def get_courses(request):
    courses = (
        Course.objects.filter(is_publish=True)
        .select_related("creator")
        .prefetch_related("chapters")
    )
    serializer = CourseSerializer(courses, many=True)
    print(serializer.data)
    for query in connection.queries:
        print(query)
    return JsonResponse({"courses": serializer.data}, status=200)
