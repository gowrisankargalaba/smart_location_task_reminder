import os
import django
from django.core.mail import send_mail
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project1.settings')
django.setup()

try:
    send_mail(
        subject="Test SmartTask",
        message="This is a test email.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['gs300@invalid.com'], # we can use the EMAIL_HOST_USER for test
        fail_silently=False,
    )
    print("Email sent successfully!")
except Exception as e:
    print(f"Error sending email: {e}")
