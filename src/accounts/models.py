import pytz
import datetime
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    image = models.ImageField(upload_to='image')

    def __str__(self):
        return str(self.user)


class Device(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    devicename = models.CharField(max_length=250)
    devicetoken = models.CharField(max_length=250, unique=True)
    devicetype = models.CharField(default='android', max_length=8)

    def __str__(self):
        return self.devicetoken


class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    date_time = models.DateTimeField(auto_now=True)

    def otp_expired(self):
        valid_up_to = (self.date_time + datetime.timedelta(minutes=5)).replace(tzinfo=pytz.UTC)
        if datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) > valid_up_to:
            return True
        else:
            return False

    def __str__(self):
        return str(self.email)
        

# User model

User._meta.get_field('email')._error_messages = {'unique':"This email has already been registered."}
User._meta.get_field('email')._unique = True

@property
def token(self):
    return str(Token.objects.get_or_create(user=self)[0])

@property
def image(self):
    return str(self.profile.image.url)

User.add_to_class('token', token)
User.add_to_class('image', image)


# Signals

from  django.db.models.signals import post_save, pre_save
from . import signals 

post_save.connect(signals.create_profile, sender=User)
pre_save.connect(signals.delete_existing_otp, sender=OTP)