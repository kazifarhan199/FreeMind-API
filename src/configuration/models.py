from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

POST_RECOMMENDATION_TYPE_LIST = (
    ('source', 'source'),
    ('social', 'social'),
    ('hybread', 'hybread'),
)


# Create your models here.
class Configuration(models.Model):
    BOT_ID = models.ForeignKey(User, models.CASCADE)
    RECOMMENDATION_TYPE = models.CharField(max_length=100, choices=POST_RECOMMENDATION_TYPE_LIST)
