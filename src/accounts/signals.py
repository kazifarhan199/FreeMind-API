from .models import Profile, OTP
from groups.models import Groups

def create_profile(sender, instance, **kwargs):
    if not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance, image='image/default_profile.jpg')
        Groups.objects.create(user=instance, group_name="Don't leave this group", is_hidden=True)

def delete_existing_otp(sender, instance, **kwargs):
    if OTP.objects.filter(email=instance.email).exists():
        OTP.objects.filter(email=instance.email).delete()

