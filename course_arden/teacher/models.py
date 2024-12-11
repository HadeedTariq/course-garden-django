from django.db import models
from authentication.models import User
from djmoney.models.fields import MoneyField


# Create your models here.
#  Models Course, Chapters, Feedback, CouponCode, Replies


class Status(models.TextChoices):
    FREE = "free", "Free"
    PAID = "paid", "Paid"


class Category(models.TextChoices):
    CS = "CS", "Computer Science"
    IT = "IT", "Information Technology"
    FS = "FS", "Full Stack"
    AD = "AD", "App Development"
    ML = "ML", "Machine Learning"
    DS = "DS", "Data Science"
    FE = "FE", "Frontend"
    BE = "BE", "Backend"
    OT = "OT", "Other"


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.CharField(max_length=255, default="fallback.webp")
    price = models.CharField(max_length=255)
    totalChapters = models.IntegerField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.FREE
    )
    is_publish = models.BooleanField(default=False)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OT
    )

    class Meta:
        db_table = "course"

    @classmethod
    def price_validation(cls, price, status):
        if status == "paid" and not price:
            return {"error": "Price is required for paid course"}
        else:
            return {"error": None}


class CourseEnrollement(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    
class CoursePurchasers(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.CharField(max_length=255)


class Chapter(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.URLField()
    chapter_number = models.PositiveIntegerField()  # Represents chapterNumber
    video = models.URLField()  # Assuming video links are stored as URLs
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="chapters"
    )

    class Meta:
        db_table = "chapter"


class CouponCode(models.Model):
    coupon = models.CharField(max_length=255)
    quantity = models.IntegerField(default=0)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="coupons",
    )
    coupon_users = models.ManyToManyField(User, related_name="used_coupons", blank=True)

    class Meta:
        db_table = "couponcode"


class Feedback(models.Model):
    content = models.TextField()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )

    class Meta:
        db_table = "feedback"


class Reply(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")
    feedback = models.ForeignKey(
        Feedback, on_delete=models.CASCADE, related_name="replies"
    )

    class Meta:
        db_table = "reply"


class CoursePoints(models.Model):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    class Meta:
        db_table = "coursepoints"
