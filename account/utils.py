from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import User


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verification_url = (
        f"http://127.0.0.1:8000/auth/"
        f"verify-email/{uid}/{token}/"
    )

    send_mail(
        subject="Verify your email",
        message=(
            f"Hello {user.username},\n\n"
            f"Please click the link below to verify your email:\n\n"
            f"{verification_url}\n\n"
            f"If you did not create this account, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
