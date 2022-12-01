from notifications.models import Notification
from groups.models import GroupsMember
from django.contrib.auth import get_user_model
from .models import PostComment
from .utils import get_estimation
from django.conf import settings
from recommendations.models import Tracker


User = get_user_model()

def postCreatedNotification(sender, instance, created, **kwargs):
    # settings.BOT_ID
    postCreatedNotification_threaded(sender, instance, created, **kwargs)

def postCreatedNotification_threaded(sender, instance, created, **kwargs):
    # Sending recommendation
    if created:
        get_estimation([instance.title, ], instance.user.id, instance.id)
        # get_estimation.delay([instance.title, ], instance.user.id, instance.id)
    # Sending notification
    if created:
        # If a new post is created 
        group_members = GroupsMember.objects.filter(group=instance.group).exclude(user=instance.user)
        notifications = []
        for group_member in group_members:
            Notification.objects.create(user=group_member.user, post=instance, post_comment=None, post_like=None, text=str(instance.user.username)+" created a new post")
    else:
        # If post has been updated 
        pass

def commentCreatedNotification(sender, instance, created, **kwargs):
    if created:
        # If a new post is created 
        team_members = GroupsMember.objects.filter(group=instance.post.group).exclude(user=instance.user)
        notifications = []
        for group_member in team_members:
            Notification.objects.create(user=group_member.user, post=instance.post, post_comment=instance, post_like=None, text=str(instance.user.username)+" commented on a post")
    else:
        # If post has been updated 
        pass

def likeCreatedNotification(sender, instance, created, **kwargs):
    if created:
        # If a new post is created 
        group_members = GroupsMember.objects.filter(group=instance.post.group, user=instance.post.user).exclude(user=instance.user)
        notifications = []
        for group_member in group_members:
            Notification.objects.create(user=group_member.user, post=instance.post, post_comment=None, post_like=instance, text=str(instance.user.username)+" liked a post")
    else:
        # If post has been updated 
        pass
