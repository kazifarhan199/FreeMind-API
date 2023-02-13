from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import signals

from posts.models import PostComment, Post
from groups.models import Groups
from configuration.models import POST_RECOMMENDATION_TYPE_LIST, Configuration

User = get_user_model()

# data points

#model to store raw data
class GarminStressData(models.Model):
    data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Garmin data collected at {self.timestamp}'

#model to store raw data
class GarminDailyData(models.Model):
    data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Garmin data collected at {self.timestamp}'

#model to store raw data
class GarminSleepData(models.Model):
    data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Garmin data collected at {self.timestamp}'


# model to store filtered  data
class DailyData(models.Model):
    is_active=models.BooleanField(default=True)
    userId =models.CharField(max_length=500)
    userAccessToken=models.CharField(max_length=500)
    summaryId=models.CharField(max_length=500)
    calendarDate=models.DateField()
    activeKilocalories = models.IntegerField(null=True)
    steps = models.IntegerField(null=True)

    durationInSeconds = models.IntegerField(null=True)
    startTimeInSeconds = models.IntegerField(null=True)
    startTimeOffsetInSeconds = models.IntegerField(null=True)

    minHeartRateInBeatsPerMinute = models.IntegerField(null=True)
    maxHeartRateInBeatsPerMinute = models.IntegerField(null=True)
    averageHeartRateInBeatsPerMinute = models.IntegerField(null=True)
    restingHeartRateInBeatsPerMinute = models.IntegerField(null=True)

    maxStressLevel = models.IntegerField(null=True)
    activityStressDurationInSeconds = models.IntegerField(null=True)
    lowStressDurationInSeconds = models.IntegerField(null=True)
    mediumStressDurationInSeconds = models.IntegerField(null=True)
    highStressDurationInSeconds = models.IntegerField(null=True)
    stressQualifier = models.CharField(max_length=200, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    
     # setting up unique keys to support receiving data for the same and not have duplicate records of same day (to aloow for update instead)
    
    # class Meta:
    #     unique_together = (("userid", "userAccessToken","calendarDate"),)
    #     index_together = (("userid", "userAccessToken","calendarDate"),)
    def __str__(self):
        return f'Garmin data collected at {self.timestamp}'

# model to store filtered  data
class SleepData(models.Model):
    is_active=models.BooleanField(default=True)
    userId =models.CharField(max_length=500)
    userAccessToken=models.CharField(max_length=500)
    summaryId=models.CharField(max_length=500)
    calendarDate=models.DateField()

    durationInSeconds= models.IntegerField(null=True)
    overallSleepScorevalue = models.IntegerField(null=True)
    overallSleepScorequalifierKey = models.CharField(max_length=200, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    
    # setting up unique keys to support receiving data for the same and not have duplicate records of same day (to aloow for update instead)
    # class Meta:
    #     unique_together = ("userid", "userAccessToken","calendarDate")
    #     index_together = ("userid", "userAccessToken","calendarDate")

    def __str__(self):
        return f'Garmin data collected at {self.timestamp}'