import pandas as pd
from surprise import KNNBasic, KNNWithMeans, KNNWithZScore, KNNBaseline, SVD, NMF
from surprise import Dataset, Reader
from groups.models import GroupsMember
from .models import Ratings, Labels, TrackerGroupRecommendation, TrackerPostRecommendation
from .utils_nlp import get_nlp_classification


def couple_source(couple):
    return couple.type.split('-')[0]


def couple_target(couple):
    return couple.type.split('-')[1]


def generatePostRecommendations(instance):
    """"
    This function generates recommedantion using preferences of the users
    If recommendation cannot be generated for any of the users, the system generates a random recommendation

    Input:
        instance = This needs to be a Post Object
    
    Output:
        recommendation = This is a recommendation

        raw_data = 
            If the system was able to generate a recommendation using the algorithm 
                (raw_outputs, context, couple_ratings, rating_for_context_dic, label_ratings, recommendation_list)
            If the recommdantion was a randomly generated recommendation
                None
    """

    # This is calculating for all laels we can recommend
    label_ratings = generateColleberativeFilteringRecommnedation(instance.user, is_label=True, is_coupuled=False)

    if label_ratings == None:
        recommendation_list = Labels.objects.filter(is_label=True, is_coupuled=False).order_by('?')
        recommendation_index = 0

        if TrackerPostRecommendation.objects.filter(user=instance.user).count() > 10:
            previous_10_recommendation_labels = [tpr.recommended for tpr in TrackerPostRecommendation.objects.filter(user=instance.user).order_by('-id')[:10]]
        else:
            previous_10_recommendation_labels = [tpr.recommended for tpr in TrackerPostRecommendation.objects.filter(user=instance.user)]

        while recommendation_list[recommendation_index] in previous_10_recommendation_labels:
                # selected recommendation alread present in the last 10 recommendations given to the user
            recommendation_index += 1
        
        if recommendation_index == len(recommendation_list):
            recommendation_index-=1


        return recommendation_list[recommendation_index], None

    # Getting context
    context, raw_outputs = get_nlp_classification(instance.title)

    # get rating for coupled labels (i.e food-food, exercise-exercise, food-exercise, ....)
    couple_ratings = generateColleberativeFilteringRecommnedation(instance.user, is_label=False, is_coupuled=True)

    # Getting the rating for current context 
    rating_for_context_dic = dict()
    for couple, rating in couple_ratings:
        if couple_source(couple) == context:
            if rating_for_context_dic.get(couple_target(couple)):
                rating_for_context_dic[couple_target(couple)] = (rating_for_context_dic[couple_target(couple)] + rating) / 2
            else:
                rating_for_context_dic[couple_target(couple)] = rating


    # This is for the question that ask about strengths and weaknesses
    # strength_ratings = generateColleberativeFilteringRecommnedation(instance.user, is_label=False, is_coupuled=False)
    recommendation_list = []
    # Adding 
    for label, target_rating in label_ratings:
        if rating_for_context_dic.get(label.type):
            recommendation_list.append([label, target_rating+rating_for_context_dic[label.type]], )
        else:
            recommendation_list.append([label, target_rating], )

    recommendation_list.sort(key=lambda x: x[1],reverse=True)

    # Avoid the 10 previously recommended activities

    if TrackerPostRecommendation.objects.filter(user=instance.user).count() > 10:
        previous_10_recommendation_labels = [tpr.recommended for tpr in TrackerPostRecommendation.objects.filter(user=instance.user).order_by('-id')[:10]]
    else:
        previous_10_recommendation_labels = [tpr.recommended for tpr in TrackerPostRecommendation.objects.filter(user=instance.user)]

    recommendation_index = 0
    while recommendation_list[recommendation_index][0] in previous_10_recommendation_labels:
            # selected recommendation alread present in the last 10 recommendations given to the user
        recommendation_index += 1
    
    if recommendation_index == len(recommendation_list):
        recommendation_index-=1

    return recommendation_list[recommendation_index][0], (raw_outputs, context, couple_ratings, rating_for_context_dic, label_ratings, recommendation_list)


def generateGroupRecommendations(group):
    """"
        This function generates recommedantion using preferences of all the users in the group
        If recommendation cannot be generated for any of the users, the system ignores that user
        If recommenadtion cannot be generated for any of the users in the group the function returns a randomly generated recommendation
        
        Input:
            group - the group
        
        Output:
            retcommendation, raw_data
    """

    user_list = [gm.user for gm in GroupsMember.objects.filter(group=group)]

    label_ratings = None
    while label_ratings == None:
        user = user_list.pop()
        label_ratings = generateColleberativeFilteringRecommnedation(user, is_label=True, is_coupuled=False, sorted=False)
        #[(l, r), (l, r), (l, r)] - user1
    
    label_ratings_track = {str(user.id)+' '+str(user): [(c.type, c.name, c.id, r) for c, r in label_ratings]}

    for user in user_list:        
        tmp_label_ratings = generateColleberativeFilteringRecommnedation(user, is_label=True, is_coupuled=False, sorted=False)
        #[(l, r), (l, r), (l, r), (l, r)] -  user 2 ..

        label_ratings_track[str(user.id)+' '+str(user)] =  [(c.type, c.name, c.id, r) for c, r in tmp_label_ratings]

        for index, (label_rating, tmp_label_rating) in enumerate(zip(label_ratings, tmp_label_ratings)): #[[(l, r), (l, r)], [(l, r), (l, r)], [(l, r), (l, r)]] - combine
            label_rating[1] = (label_rating[1] + tmp_label_rating[1]) / 2
            # [(l, r, r), (l, r, r), (l, r, r), (l, r, r), (l, r, r)]
    
    if label_ratings == None:
        return Labels.objects.filter(is_label=True, is_coupuled=False).order_by('?').first(), None
    else:
        label_ratings.sort(key=lambda x: x[1],reverse=True)
    

    recommendation_list = label_ratings
    recommendation_index = 0
    while recommendation_list[recommendation_index][0] in [tpr.recommended for tpr in TrackerGroupRecommendation.objects.filter(group=group).order_by('-id')[:10]]:
            # selected recommendation alread present in the last 10 recommendations given to the user
        recommendation_index += 1
    
    if recommendation_index == len(recommendation_list):
        recommendation_index-=1

    return recommendation_list[recommendation_index][0], (label_ratings_track, recommendation_list)


def generateColleberativeFilteringRecommnedation(user, is_label, is_coupuled, sorted=True):
    """
    Input:
        user - the user
        is_label - if we want to rate the labels that can be used as recommdantions
        is_coupled - if we want to rate the labels that have is_coupled
        sorted - should the list be sorted decending order of ratings

    Output:
        recommendations:
            If enough data is present about the user
                A list of lists of the order [[l, r], [l, r], ...] # where l - label and r - recommendation
            else
                None
    """

    ratings = []
    for rating in Ratings.objects.filter(is_active=True):
        ratings.append((rating.user.id, rating.label.id, rating.rating), )

    df = pd.DataFrame(ratings, columns=['userId', 'labelsId', 'rating'])
    
    if user.id not in df['userId'].unique():
        # print("!!!! Not enough data to generate a recommendation for ", user, "!!!!")
        return None

    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[["userId", "labelsId", "rating"]], reader)
    trainingSet = data.build_full_trainset()

    model = KNNBasic(sim_options={"user_based": False,})
    model.fit(trainingSet)

    est_ratings = []
    for label in Labels.objects.filter(is_label=is_label, is_coupuled=is_coupuled).order_by('-id'):
        rating = round(model.predict(user.id, label.id).est, 2)
        est_ratings.append([label, rating], )
    
    if sorted:
        est_ratings.sort(key=lambda x: x[1],reverse=True)
    
    return est_ratings
