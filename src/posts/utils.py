from django.conf import settings
from recommendations.models import Ratings, Labels
from surprise import KNNWithMeans
import pandas as pd
from surprise import Dataset
from surprise import Reader
import os

if not settings.USE_MODEL:
  def get_estimation(text, current_user_id):
    return Labels.objects.all().first()
    
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

  def get_estimation(text_list, current_user_id):

    predictions, raw_outputs = model.predict(text_list)
    predictions, raw_outputs

    p = predictions[0]

    for p in predictions:
      if p==0:
        pp= 'Exercise'
        prefred_labels = Labels.objects.filter(type='Food')
        other_labels = Labels.objects.exclude(type='Exercise')
      elif p == 1:
        pp= "Food"
        prefred_labels = Labels.objects.filter(type='Exercise')
        other_labels = Labels.objects.exclude(type='Food')
      else:
        pp= "general"
        prefred_labels = Labels.objects.filter(is_label=True)
        other_labels = []

    objects = Ratings.objects.filter(is_label=True).order_by('id')
    users = [i.user for i in objects]
    ratings = [i.rating for i in objects]
    labelss = [i.label.id for i in objects]

    df = pd.DataFrame(list(zip(users, labelss, ratings)), columns=['userId', 'labelsId', 'rating'])

    reader = Reader(rating_scale=(1, 5))
    # Loads Pandas dataframe
    data = Dataset.load_from_df(df[["userId", "labelsId", "rating"]], reader)

    # To use item-based cosine similarity
    sim_options = {'sim_options': {'name': 'pearson_baseline', 'min_support': 1, 'user_based': False}}

    algo = KNNWithMeans(sim_options=sim_options)

    trainingSet = data.build_full_trainset()

    algo.fit(trainingSet)

    labels = Labels.objects.all()

    scores = [(algo.predict(current_user_id, l.id).est*1.3, l.id) for l in prefred_labels]

    scores2 = [(algo.predict(current_user_id, l.id).est, l.id) for l in other_labels]

    scores += scores2
    
    predictions = scores

    predictions.sort(key=lambda x: x[0])

    label_id = predictions[0]

    label = Labels.objects.get(id=label_id[1])

    return label







