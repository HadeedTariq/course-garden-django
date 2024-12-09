from django import forms
from django.forms import ModelForm

from teacher.models import CouponCode


class CouponForm(ModelForm):
    class Meta:
        model = CouponCode
        fields = "__all__"
        widgets = {
            "coupon": forms.TextInput(attrs={"placeholder": "Enter your Coupon Code"}),
        }
        exclude = [
            "quantity",
            "course",
            "coupon_users",
        ]
