from django.db import models
from django.db.models import signals
from django.contrib.auth import get_user_model

from posts.models import Post, PostComment, PostLike

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, models.CASCADE)
    post_comment = models.ForeignKey(PostComment, models.CASCADE, null=True)
    post_like = models.ForeignKey(PostLike, models.CASCADE, null=True)
    seen = models.BooleanField(default=False)
    show = models.BooleanField(default=True)
    text = models.CharField(max_length=300)


    def __str__(self):
        return str(self.user.username)

    def get_user(self):
        if self.post_comment != None:
            return self.post_comment.user
        elif self.post_like != None:
            return self.post_like.user
        elif self.post != None:
            return self.post.user
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
            return "None"



from .signals import sendNotifications

signals.post_save.connect(sendNotifications, sender=Notification)