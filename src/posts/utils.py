from django.conf import settings
from recommendations.models import Ratings, Labels
import os

if not settings.USE_MODEL:
  def get_estimation(text):
    return text, text
    
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

  def get_estimation(text_list):

    predictions, raw_outputs = model.predict(text_list)
    predictions, raw_outputs

    p = predictions[0]

    for p in predictions:
      if p==0:
          pp= 'exercise'
      elif p == 1:
          pp= "Food"
      else:
          pp= "general"

    if pp =='exercise':
      l = Labels.objects.filter(type='Food')
    elif pp=='Food':
      l = Labels.objects.filter(type='Exercise')
    else:
      l = Labels.objects.all()

    r = l.order_by('?').first()
    return r.name, r.reason







