import json
import requests

from django.conf import settings

from accounts.models import Device


def sendNotifications(sender, instance, created, **kwargs):
    devices = Device.objects.filter(user=instance.user)

    data = {
        "click_action":"FLUTTER_NOTIFICATION_CLICK",
        "notification_id": instance.id,
        "title": instance.title,
        "body": instance.body,
        "object_id": instance.object_id,
        "send_object": instance.send_object,
        "type": instance.type
    }
    headers = {
        "Authorization":"key="+settings.FIREBASE_PROJECT_KEY,
        "Content-Type":"application/json"
    }

    for device in devices:
        response = requests.post(
            settings.FIREBASE_NOTIFICATION_URL, 
            data = json.dumps({
                "to": device.devicetoken,
                "mutable_content" : True,
                "content_available": True,
                "data": data,
                "notification": {},
            }),     
            headers = headers
        )
        
        if json.loads(response.text)['results'][0].get('error')=='NotRegistered':
            device.delete()

