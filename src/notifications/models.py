from django.db import models
from django.db.models import signals
from django.contrib.auth import get_user_model

from posts.models import Post, PostComment, PostLike

User = get_user_model()
NOTIFICATION_TYPES = (
    ("post", "post"),
    ("comment", "comment"),
    ("like", "like"),
    ("survey", "survey"),
    ("reminder", "reminder"),
)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    object_id = models.IntegerField()
    send_object = models.IntegerField()
    type = models.CharField(max_length=100, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=300)
    body = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.user.username)

    def get_user(self):
        if self.type == "" or self.type == "" or self.type == "":
            post = Post.objects.get(pk=self.send_object)
            return post.user
        return None

    def username(self):
        user = self.get_user()
        if user != None:
            return str(user.username)
        else:
            return "None"

    def user_image(self):
        user = self.get_user()
        if user != None:
            return str(user.image)
        else:
            if self.type == "survey":
                return "/media/image/default_profile.jpg"
            else:
                return "/media/image/default_profile.jpg"



from .signals import sendNotifications

signals.post_save.connect(sendNotifications, sender=Notification)