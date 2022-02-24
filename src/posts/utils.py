from django.conf import settings
import os


if not settings.USE_MODEL:
  def get_estimation(text):
    return text
    
else:
  from simpletransformers.classification import ClassificationModel, ClassificationArgs
  import torch

  model = ClassificationModel(
      settings.MODEL_NAME, settings.MODELS_PATH
  )
  def get_estimation(text_list):
    sentences = text_list
    predictions, raw_outputs = model.predict(sentences)
    predictions, raw_outputs

    predictions
    for p in predictions:
      if p==0:
          return 'exercise'
      elif p == 1:
          return "Food"
      else:
          return "general"
