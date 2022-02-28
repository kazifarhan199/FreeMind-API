from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()

class Labels(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)

class Ratings(models.Model):
    label = models.ForeignKey(Labels, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)
    rating = models.IntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
     )

