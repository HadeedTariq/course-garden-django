from celery import shared_task
from authentication.models import User
from authentication.utils import sendMail
import logging

logger = logging.getLogger(__name__)


@shared_task
def sendEmailOnCoursePurchase(student_id):
    try:

        student = User.objects.get(id=student_id)

        subject = "Course Purchase"
        message = "Thank you for purchasing the course"

        result = sendMail(subject, message, student.email)

        if result.get("success", False):
            logger.info(f"Successfully sent email to {student.email}")
        else:
            logger.error(
                f"Error sending email to {student.email}: {result.get('error', 'Unknown error')}"
            )
    except User.DoesNotExist:
        logger.error(f"No user found with ID {student_id}")
    except Exception as e:
        logger.exception(
            f"An error occurred while sending email for student ID {student_id}: {e}"
        )
