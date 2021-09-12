import posts
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import signals

from groups.models import Groups, GroupsMember

User = get_user_model()

class Post(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    group = models.ForeignKey(Groups, models.CASCADE)
    title = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)+"'s post"

    def user_image(self):
        return str(self.user.image)

    def username(self):
        return str(self.user.username)

class PostImages(models.Model):
    post = models.ForeignKey(Post, models.CASCADE)
    image = models.ImageField(upload_to='posts/')

    @property
    def image_url(self):
        return str(self.image.url)

    def __str__(self):
        return str(self.post)


class PostLike(models.Model):
    post = models.ForeignKey(Post, models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')

    def username(self):
        return str(self.user.username)

    def user_image(self):
        return str(self.user.image)

    def __str__(self):
        return str(self.user)

class PostComment(models.Model):
    post = models.ForeignKey(Post, models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, models.CASCADE)
    text = models.TextField()
    need_feadback = models.BooleanField(default=False, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def username(self):
        return str(self.user.username)

    def user_image(self):
        return str(self.user.image)

    def __str__(self):
        return str(self.text)


def image(self):
    if PostImages.objects.filter(post=self).exists():
        img = PostImages.objects.filter(post=self).first().image.url
    else:
        img = self.user.image
    return img

def images(self):
    return PostImages.objects.filter(post=self)

def like_count(self):
    return PostLike.objects.filter(post=self).count()

def comment_count(self):
    return PostComment.objects.filter(post=self).count()

Post.add_to_class('image', image)
Post.add_to_class('images', images)    
Post.add_to_class('like_count', like_count)    
Post.add_to_class('comment_count', comment_count)    
