import json
import requests

from django.conf import settings

from accounts.models import Device


def sendNotifications(sender, instance, created, **kwargs):
    devices = Device.objects.filter(user=instance.user)

    if instance.seen:
        return 

    if instance.post_like != None:
        data = {
                    "click_action":"FLUTTER_NOTIFICATION_CLICK",
                    "notification_id": instance.id,
                    "for": "likes",
                    "title": str(instance.post_like.user.username)+" like you'r post", 
                    "body": "",
                    "id": str(instance.post.id),
                }
    elif instance.post_comment != None:
        data = {
                    "click_action":"FLUTTER_NOTIFICATION_CLICK",
                    "notification_id": instance.id,
                    "for": "comment",
                    "title": str(instance.post_comment.user.username)+" commented on your post", 
                    "body": "",
                    "id": str(instance.post.id),
                }
    elif instance.post != None:
        data = {
                    "click_action":"FLUTTER_NOTIFICATION_CLICK",
                    "notification_id": instance.id,
                    "for": "home",
                    "title": str(instance.post.user.username)+" created a new post", 
                    "body": instance.post.title,
                    'id':str(instance.post.id),
                }

    for d in devices:
        re = requests.post(
            'https://fcm.googleapis.com/fcm/send', 
            data = json.dumps({
                "to": d.devicetoken,
                "mutable_content" : True,
                "content_available": True,
                "data": data,
                "notification": {
                }
            }),     
            headers = {
                "Authorization":"key="+settings.FIREBASE_PROJECT_KEY,
                "Content-Type":"application/json"
            }
        )

        if json.loads(re.text)['results'][0].get('error')=='NotRegistered':
            d.delete()