from django.db import models


class NotificationLog(models.Model):
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp')
    ]

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    sent_from = models.CharField(max_length=255)  
    sent_to = models.CharField(max_length=255)    
    message = models.TextField()
    status = models.CharField(max_length=20, default="sent")
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} from {self.sent_from} to {self.sent_to}"
