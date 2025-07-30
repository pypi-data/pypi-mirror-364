# src/notify/cli.py

import argparse
import os
import django

# Set up Django (use actual Django project's settings module)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings")
django.setup()

from notify.notify import send_email, send_whatsapp
from django.conf import settings

def main():
    parser = argparse.ArgumentParser(description="Send a notification via CLI.")
    parser.add_argument("method", choices=["email", "whatsapp"])
    parser.add_argument("recipient", help="Email or phone number")
    parser.add_argument("message", help="Message to send")
    parser.add_argument("--subject", help="Subject (for email only)", default="Notification")

    args = parser.parse_args()

    if args.method == "email":
        send_email(args.subject, args.message, args.recipient)
        print("✅ Email sent to", args.recipient)
    else:
        send_whatsapp(args.message, args.recipient)
        print("✅ WhatsApp sent to", args.recipient)
