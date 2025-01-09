from django.shortcuts import render, redirect
from .forms import UserForm, OtpForm, LoginForm, GoogleRegisterForm
from .models import User, Otp
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.contrib.auth import logout
import cloudinary
from .utils import (
    sendMail,
    upload_file,
    generate_otp,
    generate_refresh_access_token,
    validate_access_token,
    validate_refresh_token,
)
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount


def verifyUser(request):
    errormessage = ""
    successmessage = ""
    if request.method == "POST":
        otp = request.POST.get("otp")
        your_email = request.POST.get("email")
        try:
            user = Otp.objects.get(email=your_email, otp=otp)
            user.verified = True
            user.save()
            successmessage = "Congratulations for signing up"
            return redirect("/auth/login")
        except Exception as e:
            print(e)
            errormessage = "Email or OTP is incorrect"

    form = OtpForm()
    return render(
        request,
        "authentication/otp-handler.html",
        {"form": form, "errormessage": errormessage, "successmessage": successmessage},
    )


def registerUser(request):
    successmessage = ""
    errormessage = ""
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["avatar"]
            result = cloudinary.uploader.upload(file, upload_preset="ogypr3xk")
            avatar = result["secure_url"]
            username = request.POST.get("username")
            email = request.POST.get("email")
            qualification = request.POST.get("qualification")
            mobile_number = request.POST.get("mobile_number")
            country = request.POST.get("country")
            password = request.POST.get("password")
            user = User.objects.create(
                username=username,
                email=email,
                qualification=qualification,
                mobile_number=mobile_number,
                country=country,
                password=password,
                avatar=avatar,
            )
            user.save()
            subject = "Welcome to My Django App"
            otp = generate_otp()
            Otp.objects.create(
                email=email,
                otp=otp,
            )
            message = f"Hello! <b>Thank you for joining us.</b> <br> Here your otp <strong>{otp}</strong>"
            result = sendMail(subject, message, email)
            if result["success"] == True:
                successmessage += "We send an otp to your mail"
            else:
                errormessage += "Error Sending mail"
    else:
        # Otp.objects.all().delete()
        # User.objects.all().delete()
        form = UserForm()

    return render(
        request,
        "authentication/register-user.html",
        {"form": form, "successmessage": successmessage, "errormessage": errormessage},
    )


def loginUser(request):
    next_url = request.GET.get("next")
    errormessage = ""
    successmessage = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = User.objects.get(email=email)
        if user:
            is_password_correct = User.is_password_correct(password, user.password)
            if is_password_correct:
                successmessage += "Login successful"
                tokens = generate_refresh_access_token(user)
                response = HttpResponseRedirect(f"/auth/profile")
                response.set_cookie(
                    "access_token", tokens["access_token"], max_age=3600
                )
                response.set_cookie(
                    "refresh_token", tokens["refresh_token"], max_age=3600
                )
                return response

            else:
                errormessage += "Password is incorrect"
        else:
            errormessage += "User doesn't exist"

    form = LoginForm()
    # print(User.objects.update(id=6, role="teacher"))
    # user = User.objects.get(id=6)
    # user.role = "teacher"
    # user.save()

    # print(Otp.objects.all().delete())
    return render(
        request,
        "authentication/login-user.html",
        {
            "form": form,
            "errormessage": errormessage,
            "successmessage": successmessage,
            "next_url": next_url,
        },
    )


def getUser(request):
    access_token = request.COOKIES.get("access_token")
    if not access_token:
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return redirect("/auth/login")
        username = validate_refresh_token(refresh_token)
        user = User.objects.get(username=username)
        if user:
            tokens = generate_refresh_access_token(user)
            user.refresh_token = tokens["refresh_token"]
            user.save()
            display_user = {
                "username": user.username,  # Issued at time
                "email": user.email,  # Issued at time
                "qualification": user.qualification,  # Issued at time
                "avatar": user.avatar,  # Issued at time
            }
            response = render(
                request, "authentication/profile.html", {"user": display_user}
            )
            response.set_cookie("access_token", tokens["access_token"], max_age=3600)
            response.set_cookie("refresh_token", tokens["refresh_token"], max_age=3600)
            return response
    else:
        user = validate_access_token(access_token)
        return render(request, "authentication/profile.html", {"user": user})


def logout_user(
    request,
):
    response = redirect("/auth/login")
    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token")
    logout(request)
    return response


@login_required
def register_google(request):
    errormessage = ""
    successmessage = ""
    social_account = SocialAccount.objects.filter(user=request.user).first()
    if social_account:
        if request.method == "POST":
            post_data = request.POST.copy()
            extra_data = social_account.extra_data
            username = extra_data.get("name")
            email = extra_data.get("email")
            avatar = extra_data.get("picture")
            more_data = {
                "username": username,
                "email": email,
                "avatar": avatar,
                "verified": True,
            }
            post_data.update(more_data)
            form = GoogleRegisterForm(data=post_data)
            if form.is_valid():

                user_profile = form.save(commit=False)
                user_profile.username = extra_data.get("name")
                user_profile.email = extra_data.get("email")
                user_profile.avatar = extra_data.get("picture")
                user_profile.verified = True
                user_profile.save()
                tokens = generate_refresh_access_token(user_profile)
                user_profile.refresh_token = tokens["refresh_token"]
                user_profile.save()

                response = JsonResponse(
                    {"message": "User registered successfully."}, status=200
                )

                response.set_cookie(
                    "access_token", tokens["access_token"], max_age=3600
                )
                response.set_cookie(
                    "refresh_token", tokens["refresh_token"], max_age=3600 * 2
                )
                return response
            else:
                errormessage = "Invalid form data."
                form = GoogleRegisterForm()
                return render(
                    request,
                    "authentication/google-register.html",
                    {
                        "form": form,
                        "successmessage": successmessage,
                        "errormessage": errormessage,
                    },
                )

        try:
            user = User.objects.get(email=social_account.extra_data.get("email"))
            tokens = generate_refresh_access_token(user)

            response = JsonResponse(
                {"message": "User Logged In successfully."}, status=200
            )

            response.set_cookie("access_token", tokens["access_token"], max_age=3600)
            response.set_cookie(
                "refresh_token", tokens["refresh_token"], max_age=3600 * 2
            )
            return response
        except Exception as e:
            form = GoogleRegisterForm()
            return render(
                request,
                "authentication/google-register.html",
                {
                    "form": form,
                    "successmessage": successmessage,
                    "errormessage": errormessage,
                },
            )

    if not social_account:
        return JsonResponse({"error": "No social account found."}, status=404)
    else:
        form = GoogleRegisterForm()
        return render(
            request,
            "authentication/google-register.html",
            {"form": form, "successmessage": "", "errormessage": ""},
        )
