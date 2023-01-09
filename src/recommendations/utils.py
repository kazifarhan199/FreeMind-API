from django.contrib.auth import get_user_model
from posts.models import Post, PostComment
from django.conf import settings
from celery import shared_task

from .models import TrackerPostRecommendation, TrackerGroupRecommendation, SenderPostRecommendation, SenderGroupRecommendation
from .utils_generator import generatePostRecommendations, generateGroupRecommendations

User = get_user_model()

@shared_task
def sendPostRecommendations(instance_id):
    instance = SenderPostRecommendation.objects.get(pk=instance_id)
    post = instance.post
    recommendation, raw_data = generatePostRecommendations(post)

    if raw_data != None:
        nlp_raw_outputs, nlp_context, couple_ratings, rating_for_context_dic, label_ratings, recommendation_list = raw_data
    else:
        nlp_raw_outputs, nlp_context, couple_ratings, rating_for_context_dic, label_ratings, recommendation_list = "None", "None", "None", "None", "None", "None"

    comment = PostComment.objects.create(
        user=User.objects.get(pk=settings.BOT_ID), 
        post=post, 
        text=recommendation.reason, 
        need_feadback=True, 
        link=recommendation.link, 
        is_bot=True,
        label=recommendation,
    )
    
    TrackerPostRecommendation.objects.create(
        user=post.user, 

        nlp_raw_outputs=nlp_raw_outputs,
        nlp_classification=nlp_context, 
        
        estimated_rating_for_context_dic = rating_for_context_dic,
        # if raw_data is None store the string else loop over to store the neded
        estimated_couple_ratings = [(c.type, c.name, c.id, r) for c, r in couple_ratings] if raw_data!=None else couple_ratings, 
        estimated_raw_ratings_withoutcontext = [(c.type, c.name, c.id, r) for c, r in label_ratings] if raw_data!=None else label_ratings,
        estimated_final_recommendation_list = [(c.type, c.name, c.id, r) for c, r in recommendation_list] if raw_data!=None else recommendation_list,
        
        recommended = recommendation,

        comment=comment,
        sender = instance,
    )

@shared_task
def sendGroupRecommendations(instance_id):
    instance = SenderGroupRecommendation.objects.get(pk=instance_id)
    group = instance.group
    recommendation, raw_data = generateGroupRecommendations(group)

    if raw_data != None:
        label_ratings_track, recommendation_list = raw_data
    else:
        label_ratings_track, recommendation_list = "None", "None"

    post = Post.objects.create(
        user=User.objects.get(pk=settings.BOT_ID),
        group=group,
        title=recommendation.reason, 
        link=recommendation.link, 
        need_feadback=True, 
        is_recommendation=True,
    )

    TrackerGroupRecommendation.objects.create(
        group=group,
        recommended=recommendation,
        recommendation_tree= label_ratings_track, 
        recommendation_scores = [(c.type, c.name, c.id, r) for c, r in recommendation_list] if raw_data!=None else recommendation_list, 
        post=post,
        sender=instance,
        label=recommendation,
    )
