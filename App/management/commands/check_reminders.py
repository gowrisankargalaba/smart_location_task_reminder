from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from App.models import Task
import datetime
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check for tasks that are due and send reminders via Email and SMS'

    def handle(self, *args, **kwargs):
        now = datetime.datetime.now()
        current_date = now.date()
        current_time = now.time()

        tasks = Task.objects.filter(
            is_completed=False,
            is_notified=False,
            date=current_date,
            time__lte=current_time
        )

        # Twilio setup:
        # To make this work, user must configure these in settings.py or env vars
        twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        twilio_phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

        for task in tasks:
            user = task.user
            message_body = f"Reminder: Your task '{task.title}' is due now! Location keyword: {task.keyword}."

            # 1. Send Email
            if user.email:
                try:
                    send_mail(
                        subject=f"SmartTask Reminder: {task.title}",
                        message=message_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,  # Show errors so we can debug
                    )
                    self.stdout.write(self.style.SUCCESS(f"Email sent to {user.email} for task '{task.title}'"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to send email to {user.email}: {e}"))

            # 2. Send SMS via Twilio
            # (Assuming user profile has phone number, or we use a default one for demo)
            # Since standard Django user doesn't have phone, we just log it or require one in production
            # phone_number lives on the related UserProfile, not on User directly
            try:
                user_phone = user.userprofile.phone_number or None
            except Exception:
                user_phone = None
            
            if twilio_account_sid and twilio_auth_token and user_phone:
                try:
                    client = Client(twilio_account_sid, twilio_auth_token)
                    message = client.messages.create(
                        body=message_body,
                        from_=twilio_phone_number,
                        to=user_phone
                    )
                    self.stdout.write(self.style.SUCCESS(f"SMS sent to {user_phone} for task '{task.title}', SID: {message.sid}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to send SMS to {user_phone}: {e}"))
            else:
                self.stdout.write(self.style.WARNING(f"SMS not configured or missing phone for user {user.username} (Task: {task.title})"))

            # Mark as notified wrapper
            task.is_notified = True
            task.save()
