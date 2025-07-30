# src/notify/notify.py

from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client
from notify.models import NotificationLog

def send_email(subject: str, message: str, recipient_email: str):
    try:
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        NotificationLog.objects.create(
            notification_type="email",
            sent_from=settings.DEFAULT_FROM_EMAIL,
            sent_to=recipient_email,
            message=message,
            status="sent" if result else "failed"
        )
        return result
    except Exception as e:
        NotificationLog.objects.create(
            notification_type="email",
            sent_from=settings.DEFAULT_FROM_EMAIL,
            sent_to=recipient_email,
            message=message,
            status="failed"
        )
        raise e

def send_whatsapp(message: str, recipient_number: str):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            from_="whatsapp:" + settings.TWILIO_WHATSAPP_NUMBER,
            to="whatsapp:" + recipient_number,
        )
        NotificationLog.objects.create(
            notification_type="whatsapp",
            sent_from=settings.TWILIO_WHATSAPP_NUMBER,
            sent_to=recipient_number,
            message=message,
            status="sent" if msg.sid else "failed"
        )
        return msg.sid
    except Exception as e:
        NotificationLog.objects.create(
            notification_type="whatsapp",
            sent_from=settings.TWILIO_WHATSAPP_NUMBER,
            sent_to=recipient_number,
            message=message,
            status="failed"
        )
        raise e
