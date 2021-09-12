from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from .models import OTP


def check_otp_http_response_if_failed(email, otp):
    """
        This function validates the provided otp and returns
            True (bool) -> if no errors were found
                OR
            A Response obj with error message -> if incountered an error
    """

    if OTP.objects.filter(otp=otp, email=email).exists():
        otp = OTP.objects.get(otp=otp, email=email)
        if otp.otp_expired():
            return False
        else:
            return True

    else:
        return False


def send_otp_email(email, otp):
    send_mail(
        'Password Reset',
        f'Please use this pin to reset the password withing 5 min \nThe PIN is {otp}',
        settings.PROJECT_NAME,
        [email, ],
        fail_silently=False,
    )