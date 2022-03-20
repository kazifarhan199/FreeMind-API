from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()

class Labels(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    reason = models.TextField()
    link = models.CharField(max_length=400)
    is_label = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}, {self.type}'

    class Meta:
        unique_together = ('name', 'type', 'reason')

class Ratings(models.Model):
    label = models.ForeignKey(Labels, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)
    rating = models.IntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
     )
    is_label = models.BooleanField(default=True) 

    def __str__(self):
        return f'{self.label}, {self.user}'

    class Meta:
        unique_together = ('label', 'user')