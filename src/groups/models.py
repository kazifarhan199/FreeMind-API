from django.db import models
from django.db.models import signals
from django.contrib.auth import get_user_model

User = get_user_model()

class Groups(models.Model):
    group_name = models.CharField(max_length=200)
    is_hidden=models.BooleanField(default=False)
    user = models.ForeignKey(User, models.CASCADE, related_name='profilegroup')
    image = models.ImageField(default='media/image/default_profile.jpg', upload_to='groups')
    gtype = models.CharField(
        max_length = 20,
        choices = (('Default', 'Default'), ('Channel', 'Channel')),
        default = 'Default'
    )
    date_time = models.DateTimeField(auto_now_add=True)

    @property
    def is_channel(self):
        if self.gtype == 'Channel':
            return True
        else:
            return False

    def __str__(self):
        return str(self.group_name)


class GroupsMember(models.Model):
    group = models.ForeignKey(Groups, models.CASCADE, related_name='members')
    user = models.ForeignKey(User, models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)

    @property
    def username(self):
        return str(self.user.username)

    @property
    def email(self):
        return str(self.user.email)

    @property
    def userimage(self):
        return str(self.user.image)

    class Meta:
        unique_together = ('group', 'user',)


from .signals import add_creator_to_team

signals.post_save.connect(add_creator_to_team, sender=Groups)
