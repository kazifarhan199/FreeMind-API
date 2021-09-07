from .models import Profile, OTP

def create_profile(sender, instance, **kwargs):
    if not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance, image='media/image/default_profile.jpg')

def delete_existing_otp(sender, instance, **kwargs):
    if OTP.objects.filter(email=instance.email).exists():
        OTP.objects.filter(email=instance.email).delete()

