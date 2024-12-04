from django.db import models
from django.contrib.auth.hashers import check_password, make_password
from django_countries.fields import CountryField


class UserRole(models.TextChoices):
    STUDENT = "student", "Student"
    TEACHER = "teacher", "Teacher"
    ADMIN = "admin", "Admin"
    PRO = "pro", "Pro"


class Status(models.TextChoices):
    MEMBER = "member", "Member"
    PRO = "pro", "Pro"


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True)
    mobile_number = models.CharField(max_length=20, unique=True)
    avatar = models.CharField(max_length=255, default="fallback.webp")
    qualification = models.CharField(max_length=255)
    country = CountryField(blank_label="(select country)")
    password = models.CharField(max_length=255, blank=True, null=True, default=None)
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.STUDENT
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.MEMBER
    )
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = "users"

    @classmethod
    def is_password_correct(cls, user_entered_password, actual_password):
        return check_password(user_entered_password, actual_password)

    def save(self, *args, **kwargs):
        if self.password and (
            not self.pk
            or not User.objects.filter(pk=self.pk, password=self.password).exists()
        ):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


class Otp(models.Model):
    id = models.AutoField(primary_key=True)
    otp = models.IntegerField()
    email = models.EmailField(max_length=255, unique=True)

    class Meta:
        db_table = "otps"
