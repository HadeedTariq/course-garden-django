from rest_framework import serializers
from authentication.models import User
from .models import PlayList, Playlist_Course
from teacher.models import (
    Chapter,
    Course,
    CourseEnrollement,
    CoursePurchasers,
    Feedback,
    Reply,
)


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
            "is_enroll",
        ]

    def get_chapters(self, obj):
        if obj.status == "free":
            chapters = obj.chapters.all()
            return ChapterSerializer(chapters, many=True).data
        return None

    def get_is_enroll(self, obj):
        user_id = self.context["user_id"]
        if user_id:
            return CourseEnrollement.objects.filter(
                student_id_id=user_id, course_id_id=obj.id
            ).exists()
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


class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Reply
        fields = ["content", "user", "id"]


class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ["content", "user", "replies", "id"]

    def get_replies(self, obj):
        replies = obj.replies.all()
        return ReplySerializer(replies, many=True).data


class PlaylistSerializer(serializers.ModelSerializer):
    course_exist = serializers.SerializerMethodField()

    class Meta:
        model = PlayList
        fields = ["title", "user", "type", "id", "course_exist"]

    def get_course_exist(self, obj):
        return Playlist_Course.objects.filter(
            course_id=self.context["course_id"], playlist_id=obj.id
        ).exists()
