import json
import requests

from django.conf import settings

from accounts.models import Device


def sendNotifications(sender, instance, created, **kwargs):
    if instance.survey:
        sendSurveyNotifications(sender, instance, created, **kwargs)
        return 
    else:
        sendPostNotifications(sender, instance, created, **kwargs)
        return


def sendPostNotifications(sender, instance, created, **kwargs):
    devices = Device.objects.filter(user=instance.user)
    if instance.post_like != None:
        data = {
            "click_action":"FLUTTER_NOTIFICATION_CLICK",
            "notification_id": instance.id,
            "title": instance.text, 
            "body": "",
            "post": str(instance.post.id),
        }
    elif instance.post_comment != None:
        data = {
            "click_action":"FLUTTER_NOTIFICATION_CLICK",
            "notification_id": instance.id,
            "title": instance.text, 
            "body": instance.post_comment.text,
            "post": str(instance.post.id),
        }
    elif instance.post != None:
        data = {
            "click_action":"FLUTTER_NOTIFICATION_CLICK",
            "notification_id": instance.id,
            "title": instance.text, 
            "body": instance.post.title,
            'post':str(instance.post.id),
        }

    for device in devices:
        response = requests.post(
            'https://fcm.googleapis.com/fcm/send', 
            data = json.dumps({
                "to": device.devicetoken,
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
        
        if json.loads(response.text)['results'][0].get('error')=='NotRegistered':
            device.delete()


def sendSurveyNotifications(sender, instance, created, **kwargs):
    devices = Device.objects.filter(user=instance.user)
    data = {
        "click_action":"FLUTTER_NOTIFICATION_CLICK",
        "notification_id": instance.id,
        "title": instance.text, 
        "body": "",
        "post": 0,
        "survey": True
    }

    for device in devices:
        response = requests.post(
            'https://fcm.googleapis.com/fcm/send', 
            data = json.dumps({
                "to": device.devicetoken,
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

        if json.loads(response.text)['results'][0].get('error')=='NotRegistered':
            device.delete()