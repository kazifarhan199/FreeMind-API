from django.conf import settings
from simpletransformers.classification import ClassificationModel, ClassificationArgs
import numpy as np

model_args = ClassificationArgs(
    num_train_epochs=1,
    overwrite_output_dir=True,
    evaluate_during_training=True,
)
model = ClassificationModel(
    settings.MODEL_NAME, settings.MODELS_PATH
)

pred_label = {0:'Exercise', 1:'Food', 2:'general', 3: 'Stress'}

def get_nlp_classification(text):
    text_list = [text]
    predictions, raw_outputs = model.predict(text_list)
    prediction = predictions[0]

    label = pred_label[prediction]

    return label, raw_outputs
