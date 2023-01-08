from .utils import sendPostRecommendations, sendGroupRecommendations
from posts.models import Post

def sendGroupRecommendationsSignal(sender, instance, *args, **kwargs):
    if instance.group:
        sendGroupRecommendations(instance)
        return 
    else:
        print("No group specified")


def sendPostRecommendationsSignal(sender, instance, *args, **kwargs):
    sendPostRecommendations(instance)
    
