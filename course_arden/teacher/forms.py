from django.forms import ModelForm
from django import forms
from .models import Course, Chapter, CouponCode


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
        fields = "__all__"
        widgets = {
            "thumbnail": forms.FileInput(attrs={"placeholder": "Upload thumbnail"}),
            "video": forms.FileInput(
                attrs={"accept": "video/*", "placeholder": "Upload video"},
            ),
        }
        exclude = [
            "course",
        ]


class CouponForm(ModelForm):
    class Meta:
        model = CouponCode
        fields = "__all__"

        exclude = [
            "course",
            "coupon_users",
        ]
