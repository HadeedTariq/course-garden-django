from django.forms import ModelForm
from django import forms
from .models import User, Otp


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        widgets = {
            "password": forms.PasswordInput(attrs={"placeholder": "Enter Password"}),
            "mobile_number": forms.NumberInput(
                attrs={"placeholder": "Enter Mobile Number"}
            ),
            "avatar": forms.FileInput(attrs={"placeholder": "Upload Avatar"}),
        }
        exclude = [
            "refresh_token",
            "role",
            "status",
            "verified",
        ]


class OtpForm(ModelForm):
    class Meta:
        model = Otp
        fields = ["otp", "email"]
        widgets = {
            "otp": forms.NumberInput(attrs={"placeholder": "Enter the otp"}),
            "email": forms.EmailInput(attrs={"placeholder": "Enter your email also"}),
        }


class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ["email", "password"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "Enter your email "}),
            "password": forms.PasswordInput(
                attrs={"placeholder": "Enter your password"}
            ),
        }


class GoogleRegisterForm(ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        widgets = {
            "mobile_number": forms.NumberInput(
                attrs={"placeholder": "Enter Mobile Number"}
            ),
        }
        exclude = [
            "refresh_token",
            "role",
            "status",
            "verified",
            "username",
            "email",
            "avatar",
            "password",
        ]
