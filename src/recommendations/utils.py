from django.contrib.auth import get_user_model
from posts.models import Post, PostComment
from django.conf import settings
from celery import shared_task
from groups.models import GroupsMember, Groups

from .models import TrackerPostRecommendation, TrackerGroupRecommendation, SenderPostRecommendation, SenderGroupRecommendation, TrackerWearableRecommendation, SenderWearableRecommendation
from .utils_generator import generatePostRecommendations, generateGroupRecommendations, generateWearableRecommendations, sort_key_take_rating
from configuration.models import Configuration, POST_RECOMMENDATION_TYPE_LIST

User = get_user_model()


@shared_task
def sendPostRecommendations(instance_id, config_id):
    configurations = Configuration.objects.get(pk=config_id)

    instance = SenderPostRecommendation.objects.get(pk=instance_id)
    post = instance.post
    recommendation, raw_data = generatePostRecommendations(post)

    if raw_data != None:
        nlp_raw_outputs, nlp_context, couple_ratings, rating_for_context_dic, label_ratings, recommendation_list = raw_data
    else:
        nlp_raw_outputs, nlp_context, couple_ratings, rating_for_context_dic, label_ratings, recommendation_list = "None", "None", "None", "None", "None", "None"

    comment = PostComment.objects.create(
        user=User.objects.get(pk=configurations.BOT_ID.id), 
        post=post, 
        text=recommendation.source_based,
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

        recommendation_type=configurations.RECOMMENDATION_TYPE,
        configurations=configurations,
    )


@shared_task
def sendPostRecommendationsSocial(instance_id, config_id):
    configurations = Configuration.objects.get(pk=config_id)

    instance = SenderPostRecommendation.objects.get(pk=instance_id)
    post = instance.post
    group = instance.post.group
    user_list = [gm.user for gm in GroupsMember.objects.filter(group = group)]
    tmp_user = post.user

    recommendation_list_list = []
    nlp_context_list = []
    nlp_raw_outputs_list = []
    rating_for_context_dic_list = []
    label_ratings_list = []
    couple_ratings_list = []

    for user in user_list:
        post.user = user
        recommendation, raw_data = generatePostRecommendations(post)

        if raw_data != None:
            nlp_raw_outputs, nlp_context, couple_ratings, rating_for_context_dic, label_ratings, recommendation_list = raw_data
        else:
            nlp_raw_outputs, nlp_context, couple_ratings, rating_for_context_dic, label_ratings, recommendation_list = "None", "None", "None", "None", "None", []
    
        if raw_data != None:
            recommendation_list.sort(key=lambda x: x[0].id, reverse=True)

            if recommendation_list_list == []:
                recommendation_list_list = recommendation_list
            else:
                for rec_list, (l, r) in zip(recommendation_list_list, recommendation_list):
                    rec_list[1] = rec_list[1]+r
        
        nlp_raw_outputs_list.append(nlp_raw_outputs)
        nlp_context_list.append(nlp_context)
        couple_ratings_list.append(couple_ratings)
        rating_for_context_dic_list.append(rating_for_context_dic)
        label_ratings_list.append(label_ratings)
        
    post.user = tmp_user
    
    recommendation_list_list.sort(key=lambda x: x[1], reverse=True)
    
    recommendation_list = recommendation_list_list
    recommendation_index = 0

    if TrackerGroupRecommendation.objects.filter(group=group).count() > 10:
        previous_10_recommendation_labels = [tpr.recommended for tpr in TrackerGroupRecommendation.objects.filter(group=group).order_by('-id')[:10]]
    else:
        previous_10_recommendation_labels = [tpr.recommended for tpr in TrackerGroupRecommendation.objects.filter(group=group)]

    while recommendation_list[recommendation_index][0] in previous_10_recommendation_labels:
            # selected recommendation alread present in the last 10 recommendations given to the group 
            # (as we are combining recommednations for all users in group hrere)
        recommendation_index += 1
    
    if recommendation_index == len(recommendation_list):
        recommendation_index-=1

    recommendation = recommendation_list[recommendation_index][0]

    if configurations.RECOMMENDATION_TYPE == POST_RECOMMENDATION_TYPE_LIST[1][0]:
        comment = PostComment.objects.create(
            user=User.objects.get(pk=configurations.BOT_ID.id), 
            post=post, 
            text=recommendation.social_based, 
            need_feadback=True, 
            link=recommendation.link, 
            is_bot=True,
            label=recommendation,
        )
    else:
        comment = PostComment.objects.create(
            user=User.objects.get(pk=configurations.BOT_ID.id), 
            post=post, 
            text=recommendation.hybrid_based, 
            need_feadback=True, 
            link=recommendation.link, 
            is_bot=True,
            label=recommendation,
        )
    
    TrackerPostRecommendation.objects.create(
        user=post.user, 

        nlp_raw_outputs=nlp_raw_outputs_list,
        nlp_classification=nlp_context_list, 
        
        estimated_rating_for_context_dic = rating_for_context_dic_list,
        # if raw_data is None store the string else loop over to store the neded
        estimated_couple_ratings = couple_ratings_list,
        estimated_raw_ratings_withoutcontext = label_ratings_list,
        estimated_final_recommendation_list = [(c.type, c.name, c.id, r) for c, r in recommendation_list_list] if raw_data!=None else recommendation_list,
        
        recommended = recommendation,

        comment=comment,
        sender = instance,

        recommendation_type=configurations.RECOMMENDATION_TYPE,
        configurations=configurations,
    )


@shared_task
def sendGroupRecommendations(instance_id, config_id):
    configurations = Configuration.objects.get(pk=config_id)    

    instance = SenderGroupRecommendation.objects.get(pk=instance_id)
    group = instance.group
    recommendation, raw_data = generateGroupRecommendations(group)

    if raw_data != None:
        label_ratings_track, recommendation_list = raw_data
    else:
        label_ratings_track, recommendation_list = "None", "None"

    post = Post.objects.create(
        user=User.objects.get(pk=configurations.BOT_ID.id),
        group=group,
        title=recommendation.group_based, 
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
        recommendation_type=configurations.RECOMMENDATION_TYPE,
        configurations=configurations,
    )


@shared_task
def sendWearableRecommendations(instance_id, config_id):
    configurations = Configuration.objects.get(pk=config_id)    

    instance = SenderWearableRecommendation.objects.get(pk=instance_id)
    user = instance.user
    recommendation, reason,  raw_data = generateWearableRecommendations(user)



    if raw_data != None:
        label_ratings_track, recommendation_list = raw_data
        #print("label_ratings_track")
        #print(label_ratings_track)
        print("\n\nrecommendation_list ")
        print(recommendation_list)
        sorted_recommendation_list =sorted(recommendation_list,key=sort_key_take_rating)
        print("\n\n sorted recommendation_list ")
        print( sorted_recommendation_list)
        print("\n\n!!!!!!!!!!!!!!")
        print( sorted_recommendation_list[-1])
        print("sorted label_ratings_track")
        sorted_label_track =sorted(label_ratings_track,key=sort_key_take_rating)
        print(sorted_label_track)
        print("\n\n!!!!!!!!!!!!!!")
        print(sorted_label_track[-1])
    else:
        label_ratings_track, recommendation_list = "None", "None"

    if (instance.optimal):
        final_reason= "You did a great job! "+"\n\nRecommendation: "+ recommendation.source_based +"\n\n\nReason: "+recommendation.type +": "+ reason
    else:
        final_reason= "Recommendation: "+ recommendation.source_based +"\n\n\nReason: "+recommendation.type +": "+ reason

    post = Post.objects.create(
        user=User.objects.get(pk=configurations.BOT_ID.id),
        group=instance.user.group,
        title=final_reason, 
        link=recommendation.link, 
        need_feadback=True, 
        is_recommendation=True,
    )

    TrackerWearableRecommendation.objects.create(
        user=instance.user,
        recommended=recommendation,
        recommendation_tree= label_ratings_track, 
        recommendation_scores = [(c.type, c.name, c.id, r) for c, r in recommendation_list] if raw_data!=None else recommendation_list, 
        post=post,
        sender=instance,
        recommendation_type=configurations.RECOMMENDATION_TYPE,
        configurations=configurations,
    )