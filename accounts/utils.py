# accounts/utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_email(subject, message, recipient):
   
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "obomaish@gmail.com")
    
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[recipient],
        fail_silently=False,
    )
