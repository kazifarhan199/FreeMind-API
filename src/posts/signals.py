from notifications.models import Notification
from groups.models import GroupsMember
from django.contrib.auth import get_user_model
from .models import PostComment
from .utils import get_estimation
from django.conf import settings
import threading

User = get_user_model()

def postCreatedNotification(sender, instance, created, **kwargs):
    start_time = threading.Timer(settings.BOT_ID, lambda : postCreatedNotification_threaded(sender, instance, created, **kwargs))
    start_time.start()

def postCreatedNotification_threaded(sender, instance, created, **kwargs):
    # Sending recommendation
    if created:
        label = get_estimation([instance.title, ], instance.user)
        # Ussing Bot user to send notifications
        # try:
        PostComment.objects.create(user=User.objects.get(pk=settings.BOT_ID), post=instance, text=label.reason, need_feadback=True, link=label.link)
        # except:
        #     print("Fix the bot id !!!")
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
