import datetime
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_task_reminders():
    """Runs every minute — checks for due tasks and sends email reminders."""
    try:
        # Import here to avoid AppRegistry not ready errors
        from App.models import Task
        from twilio.rest import Client

        now = datetime.datetime.now()
        current_date = now.date()
        current_time = now.time()

        tasks = Task.objects.filter(
            is_completed=False,
            is_notified=False,
            date=current_date,
            time__lte=current_time
        )

        twilio_sid   = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        twilio_from  = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

        for task in tasks:
            user = task.user
            message_body = (
                f"Reminder: Your task '{task.title}' is due now! "
                f"Location keyword: {task.keyword}."
            )

            # --- Send Email ---
            if user.email:
                try:
                    send_mail(
                        subject=f"SmartTask Reminder: {task.title}",
                        message=message_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    logger.info(f"[Scheduler] Email sent to {user.email} for '{task.title}'")
                except Exception as e:
                    logger.error(f"[Scheduler] Email failed for {user.email}: {e}")

            # --- Send SMS via Twilio ---
            try:
                user_phone = user.userprofile.phone_number or None
            except Exception:
                user_phone = None

            if twilio_sid and twilio_token and user_phone:
                try:
                    client = Client(twilio_sid, twilio_token)
                    client.messages.create(
                        body=message_body,
                        from_=twilio_from,
                        to=user_phone
                    )
                    logger.info(f"[Scheduler] SMS sent to {user_phone} for '{task.title}'")
                except Exception as e:
                    logger.error(f"[Scheduler] SMS failed for {user_phone}: {e}")

            # Mark notified so it won't fire again
            task.is_notified = True
            task.save()

    except Exception as e:
        logger.error(f"[Scheduler] Unexpected error in send_task_reminders: {e}")
