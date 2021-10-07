from notifications.models import Notification
from groups.models import GroupsMember

from .models import PostComment

def postCreatedNotification(sender, instance, created, **kwargs):
    
    if created:
        # If a new post is created 
        group_members = GroupsMember.objects.filter(group=instance.group).exclude(user=instance.user)
        notifications = []
        for group_member in group_members:
            Notification.objects.create(user=group_member.user, post=instance, post_comment=None, post_like=None)
    else:
        # If post has been updated 
        pass

def commentCreatedNotification(sender, instance, created, **kwargs):
    if created:
        # If a new post is created 
        team_members = GroupsMember.objects.filter(group=instance.post.group).exclude(user=instance.user)
        notifications = []
        for group_member in team_members:
            Notification.objects.create(user=group_member.user, post=instance.post, post_comment=instance, post_like=None)
    else:
        # If post has been updated 
        pass

def likeCreatedNotification(sender, instance, created, **kwargs):
    if created:
        # If a new post is created 
        group_members = GroupsMember.objects.filter(group=instance.post.group, user=instance.post.user).exclude(user=instance.user)
        notifications = []
        for group_member in group_members:
            Notification.objects.create(user=group_member.user, post=instance.post, post_comment=None, post_like=instance)
    else:
        # If post has been updated 
        pass