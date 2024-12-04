from django.forms import ModelForm
from django import forms
from .models import Course, Chapter


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = "__all__"
        widgets = {
            "thumbnail": forms.FileInput(attrs={"placeholder": "Upload thumbnail"}),
        }
        exclude = [
            "creator",
            "is_publish",
        ]


class ChapterForm(ModelForm):
    class Meta:
        model = Chapter
        fields = ["title", "description", "thumbnail", "chapter_number", "video"]
