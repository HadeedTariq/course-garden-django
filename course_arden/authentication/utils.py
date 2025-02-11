from django.core.mail import EmailMessage

import os

from django.shortcuts import redirect
from course_arden.utils import generate_random_string
from django.conf import settings
import secrets
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


def upload_file(uploaded_file):
    random_string = generate_random_string()
    file_name = str(uploaded_file.name).replace(" ", "-")
    save_path = os.path.join(
        settings.MEDIA_ROOT,
        "uploads",
        f"{random_string}-{file_name}",
    )
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    avatar = (f"uploads/{random_string}-{file_name}",)
    return avatar


def generate_otp():
    otp = secrets.randbelow(10**6)  # Generates a random number between 0 and 999999
    otp = str(otp).zfill(
        6
    )  # Ensure the OTP is always 6 digits (pads with leading zeros if needed)
    return otp


def generate_refresh_access_token(user):

    access_payload = {
        "username": user.username,  # Issued at time
        "email": user.email,  # Issued at time
        "qualification": user.qualification,  # Issued at time
        "avatar": user.avatar,  # Issued at time
        "id": user.id,  # Issued at time
    }
    refresh_payload = {"id": user.id}

    access_token = jwt.encode(
        access_payload,
        settings.JWT_ACCESS_TOKEN_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_REFRESH_TOKEN_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return {"refresh_token": refresh_token, "access_token": access_token}


def validate_access_token(token):
    try:
        user = jwt.decode(
            token,
            settings.JWT_ACCESS_TOKEN_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return user
    except ExpiredSignatureError:
        raise ValueError("Token has expired.")
    except InvalidTokenError:
        raise ValueError("Invalid token.")


def validate_refresh_token(token):
    try:
        user = jwt.decode(
            token,
            settings.JWT_REFRESH_TOKEN_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return user["username"]
    except ExpiredSignatureError:
        raise ValueError("Token has expired.")
    except InvalidTokenError:
        raise ValueError("Invalid token.")


def sendMail(subject, message, email):
    email_message = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [email])
    try:
        email_message.content_subtype = "html"
        email_message.send()
        return {"success": True}
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"success": False}
