from django.contrib import admin
from .models import Profile, OTP, Device

admin.site.register(Profile)
admin.site.register(OTP)
admin.site.register(Device)
