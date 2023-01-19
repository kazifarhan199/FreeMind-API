from .utils import sendPostRecommendations, sendGroupRecommendations, sendPostRecommendationsSocial
from posts.models import Post
from configuration.models import Configuration, POST_RECOMMENDATION_TYPE_LIST


def sendGroupRecommendationsSignal(sender, instance, *args, **kwargs):
    configurations = Configuration.objects.filter(group=instance.group).order_by('-id').first()
    if configurations == None:
        print("\n\n\n\t\t!!!!!Clease create configurations in admin!!!!!\n\n\n.")
        configurations = Configuration.objects.all().order_by('-id').first()
    print(configurations)
    config_id = configurations.id

    if instance.group:
        sendGroupRecommendations.delay(instance.id, config_id)
        # sendGroupRecommendations(instance)
        return 
    else:
        print("No group specified")


def sendPostRecommendationsSignal(sender, instance, *args, **kwargs):
    configurations = Configuration.objects.filter(group=instance.post.group).order_by('-id').first()
    if configurations == None:
        print("\n\n\n\t\t!!!!!Clease create configurations in admin!!!!!\n\n\n.")
        configurations = Configuration.objects.all().order_by('-id').first()

    print(configurations)
    config_id = configurations.id

    if configurations.RECOMMENDATION_TYPE == POST_RECOMMENDATION_TYPE_LIST[0][0]: # Source
        sendPostRecommendations.delay(instance.id, config_id)

    if configurations.RECOMMENDATION_TYPE == POST_RECOMMENDATION_TYPE_LIST[1][0]: # Social
        sendPostRecommendationsSocial.delay(instance.id, config_id)

    if configurations.RECOMMENDATION_TYPE == POST_RECOMMENDATION_TYPE_LIST[2][0]: # Hybread
        sendPostRecommendationsSocial.delay(instance.id, config_id)

    