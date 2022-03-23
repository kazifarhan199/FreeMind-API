from django.conf import settings
from recommendations.models import Ratings, Labels
from surprise import NMF
import pandas as pd
from surprise import Dataset
from surprise import Reader
import os
import random

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
    print('Predictions are ', predictions)

    d = {0:'Exercise', 1:'Food', 2:'general', 3: 'Stress'}
    NLP_model_prediction = d.get(predictions[0])
    print("The predicted catagory is", NLP_model_prediction)
    d_values = list(d.values())


    label_scores = get_label_scores_recommendation(current_user) # tuple(predict rating, label object)
    label_type_scores = get_label_type_questiosn_scores_recommendation(current_user) # tuple(predict rating, label object)
    
    print(label_scores)
    for typelabel_score in label_type_scores:

      for index in range(len(label_scores)):
      
        if (label_scores[index][-1].type == typelabel_score[-1].type):

          label_scores[index][0] = label_scores[index][0] + typelabel_score[0]
        
        elif(len(typelabel_score[-1].type.split('-')) == 2 and label_scores[index][-1].type == typelabel_score[-1].type.split('-')[1] and typelabel_score[-1].type.split('-')[0]==NLP_model_prediction):
          label_scores[index][0] = label_scores[index][0] + typelabel_score[0]


    label_scores.sort(key=lambda x: x[0],reverse=True)
    label_id = label_scores[:10][random.randrange(1, 10)]

    label = Labels.objects.get(id=label_id[1].id)

    scores = [(ls[0], ls[1].id) for ls in label_scores]

    print(scores)

    return label, NLP_model_prediction, scores



def get_label_scores_recommendation(current_user, ):
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

    all_labels = Labels.objects.filter(is_label=True)
    scores = [list((round(algo.predict(current_user.id, l.id).est, 2), l)) for l in all_labels]
    scores.sort(key=lambda x: x[0],reverse=True)

    return scores

def get_label_type_questiosn_scores_recommendation(current_user, ):
    objects = Ratings.objects.filter(is_label=False).order_by('id')
    users = [i.user.id for i in objects]
    ratings = [(6-i.rating)/3 for i in objects]
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

    