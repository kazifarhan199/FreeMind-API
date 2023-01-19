from django.db import models
from django.contrib.auth import get_user_model

from groups.models import Groups

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
    group = models.ForeignKey(Groups, models.CASCADE)
    date_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.group) + ' ==> ' + str(self.RECOMMENDATION_TYPE)
