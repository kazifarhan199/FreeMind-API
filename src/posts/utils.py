from django.conf import settings
from recommendations.models import Ratings, Labels, Tracker
from surprise import NMF
import pandas as pd
from surprise import Dataset
from surprise import Reader
import os
import random
from copy import deepcopy

if not settings.USE_MODEL:
  def get_estimation(text, current_user):
    return Labels.objects.all().first(), "NLP_model_prediction", ["This is just a demo"]
    
else:
  from simpletransformers.classification import ClassificationModel, ClassificationArgs
  import torch

  model_args = ClassificationArgs(
      num_train_epochs=1,
      overwrite_output_dir=True,
      evaluate_during_training=True,
  )

  model = ClassificationModel(
      settings.MODEL_NAME, settings.MODELS_PATH
  )

  def get_estimation(text_list, current_user):

    predictions, raw_outputs = model.predict(text_list)
    # print('Predictions are ', predictions)

    d = {0:'Exercise', 1:'Food', 2:'general', 3: 'Stress'}
    NLP_model_prediction = d.get(predictions[0])
    # print("The predicted catagory is", NLP_model_prediction)
    d_values = list(d.values())

    showed_label = [t.label.id for t in Tracker.objects.filter(user=current_user).order_by('-id')][:10 if len(Tracker.objects.filter(user=current_user))>10 else len(Tracker.objects.filter(user=current_user))]
    all_labels = Labels.objects.filter(is_label=True).exclude(id__in=showed_label)

    label_scores = get_label_scores_recommendation(current_user, all_labels) # tuple(predict rating, label object)
    label_type_scores = get_label_type_questiosn_scores_recommendation(current_user) # tuple(predict rating, label object)
    
    new_label_scores = deepcopy(label_scores)

    for typelabel_score in label_type_scores:

      for index in range(len(new_label_scores)):
      
        if (new_label_scores[index][-1].type == typelabel_score[-1].type):

          new_label_scores[index][0] = new_label_scores[index][0] + typelabel_score[0]
        
        elif(len(typelabel_score[-1].type.split('-')) == 2 and label_scores[index][-1].type == typelabel_score[-1].type.split('-')[1] and typelabel_score[-1].type.split('-')[0]==NLP_model_prediction):
          new_label_scores[index][0] = new_label_scores[index][0] + typelabel_score[0]


    new_label_scores.sort(key=lambda x: x[0],reverse=True)
    label_id = new_label_scores[:10 if len(new_label_scores)>10 else len(new_label_scores)][random.randrange(1, 10 if len(new_label_scores)>10 else len(new_label_scores))]

    label = Labels.objects.get(id=label_id[1].id)

    label_scores = [(ls[0], ls[1].id, ls[1].name) for ls in label_scores]
    label_type_scores = [(ls[0], ls[1].id, ls[1].name) for ls in label_type_scores]
    new_label_scores = [(ls[0], ls[1].id, ls[1].name) for ls in new_label_scores]

    return label, NLP_model_prediction, label_scores, label_type_scores, new_label_scores



def get_label_scores_recommendation(current_user, all_labels):
    objects = Ratings.objects.filter(is_label=True).order_by('id')
    
    users = [i.user.id for i in objects]
    ratings = [i.rating for i in objects]
    labels = [i.label.id for i in objects]
    df = pd.DataFrame(list(zip(users, labels, ratings)), columns=['userId', 'labelsId', 'rating'])

    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[["userId", "labelsId", "rating"]], reader)
    trainingSet = data.build_full_trainset()
    algo = NMF()
    algo.fit(trainingSet)

    scores = [list((round(algo.predict(current_user.id, l.id).est, 2), l)) for l in all_labels]
    scores.sort(key=lambda x: x[0],reverse=True)

    return scores

def get_label_type_questiosn_scores_recommendation(current_user, ):

    objects = Ratings.objects.filter(is_label=False).order_by('id')
    users = [i.user.id for i in objects]
    ratings = [(6-i.rating)/3 if i.label.is_coupuled==False else (i.rating)/2 for i in objects]
    labels = [i.label.id for i in objects]
    df = pd.DataFrame(list(zip(users, labels, ratings)), columns=['userId', 'labelsId', 'rating'])

    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[["userId", "labelsId", "rating"]], reader)
    trainingSet = data.build_full_trainset()
    algo = NMF()
    algo.fit(trainingSet)

    all_labels = Labels.objects.filter(is_label=False)
    scores = [list((round(algo.predict(current_user.id, l.id).est, 2), l)) for l in all_labels]
    scores.sort(key=lambda x: x[0],reverse=True)

    return scores

    