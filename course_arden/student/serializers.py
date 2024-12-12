from rest_framework import serializers
from authentication.models import User
from teacher.models import Chapter, Course, CourseEnrollement, CoursePurchasers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "avatar", "id"]

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ["title", "description", "thumbnail", "chapter_number", "video"]


class CourseSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    chapters = serializers.SerializerMethodField()
    is_enroll = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "creator",
            "chapters",
            "thumbnail",
            "price",
            "category",
            "status",
            "is_enroll"
        ]

    def get_chapters(self, obj):
        if obj.status == "free":
            chapters = obj.chapters.all()
            return ChapterSerializer(chapters, many=True).data
        return None
    def get_is_enroll(self, obj):
        user_id = self.context['user_id']
        if user_id:
            return CourseEnrollement.objects.filter(student_id_id=user_id,course_id_id=obj.id).exists()
        else:
            return False


class PaidCourseSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    chapters = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "creator",
            "chapters",
            "thumbnail",
            "price",
            "category",
            "status",
        ]

    def get_chapters(self, obj):
        chapters = obj.chapters.all()
        return ChapterSerializer(chapters, many=True).data
        
class PurchaseCourseSerializer(serializers.ModelSerializer):
    course_id = PaidCourseSerializer()
    class Meta:
        model = CoursePurchasers
        fields = ["course_id"]
