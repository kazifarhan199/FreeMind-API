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
    print(p)

    return p, p







