from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.utils import sendMail
from teacher.models import CoursePurchasers
from authentication.models import User


@receiver(post_save, sender=CoursePurchasers)
def send_course_purchaser_email(sender, instance, created, **kwargs):
    if created:
        student = User.objects.filter(id=instance.student_id.id).first()
        print(student.email)
        subject = "Course Purchase"
        message = f"Thank you for purchasing the course"
        result = sendMail(subject, message, student.email)
        if result["success"] == True:
            print("successfully sent mail to student")
        else:
            print("Error Sending mail")
