from django.contrib import admin

# Register your models here.
from .models import GarminStressData,GarminDailyData,GarminSleepData,DailyData,SleepData, UserIdMap

admin.site.register(GarminStressData)
admin.site.register(GarminDailyData)
admin.site.register(GarminSleepData)
admin.site.register(DailyData)
admin.site.register(SleepData)
admin.site.register(UserIdMap)
