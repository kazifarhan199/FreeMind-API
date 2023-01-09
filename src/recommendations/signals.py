from .utils import sendPostRecommendations, sendGroupRecommendations
from posts.models import Post

def sendGroupRecommendationsSignal(sender, instance, *args, **kwargs):
    if instance.group:
        sendGroupRecommendations.delay(instance.id)
        # sendGroupRecommendations(instance)
        return 
    else:
        print("No group specified")


def sendPostRecommendationsSignal(sender, instance, *args, **kwargs):
    sendPostRecommendations.delay(instance.id)

    