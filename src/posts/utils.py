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

    if (NLP_model_prediction=='Exercise'):
      priority = Labels.objects.filter(type='Food', is_label=True)
      others = Labels.objects.exclude(type='Food', is_label=True)
    elif (NLP_model_prediction=='Food'):
      priority = Labels.objects.filter(type='Exercise', is_label=True)
      others = Labels.objects.exclude(type='Exercise', is_label=True)
    elif (NLP_model_prediction=='Stress'):
      priority = Labels.objects.filter(type='Stress', is_label=True)
      others = Labels.objects.exclude(type='Stress', is_label=True)
    else:
      priority = []
      others = Labels.objects.filter(is_label=True)

    objects = Ratings.objects.filter(is_label=True).order_by('id')
    users = [i.user.id for i in objects]
    ratings = [i.rating for i in objects]
    labelss = [i.label.id for i in objects]
    df = pd.DataFrame(list(zip(users, labelss, ratings)), columns=['userId', 'labelsId', 'rating'])

    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[["userId", "labelsId", "rating"]], reader)
    trainingSet = data.build_full_trainset()
    algo = NMF()
    algo.fit(trainingSet)

    labels = Labels.objects.all()
    scores = [(algo.predict(current_user.id, l.id).est*1.3, l.id) for l in priority]
    scores2 = [(algo.predict(current_user.id, l.id).est, l.id) for l in others]


    scores += scores2

    print("Scores are ", scores)
    
    predictions = scores

    predictions.sort(key=lambda x: x[0],reverse=True)

    print("Scores are ", scores)

    label_id = predictions[:10][random.randrange(1, 11)]

    label = Labels.objects.get(id=label_id[1])

    return label, NLP_model_prediction, scores







