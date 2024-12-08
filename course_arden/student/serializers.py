from rest_framework import serializers
from authentication.models import User
from teacher.models import Chapter, Course


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
        if obj.status == "free":
            chapters = obj.chapters.all()
            return ChapterSerializer(chapters, many=True).data
        return None
