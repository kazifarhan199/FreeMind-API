from django.urls import path, include
from . import views 

urlpatterns = [
    path('', views.QuestionsListView.as_view(), name='labels'),
    path('labels/', views.LabelsListView.as_view(), name='labels'),
    path('copuled/', views.QuestionsCopuledListView.as_view(), name='copuled'),
    path('label/create/', views.LabelsCreateView.as_view(), name='labels-create'),
    path('label/edit/', views.LablesUpdateView.as_view(), name='labels-edit'),
    path('rating/', views.RecommendationsView.as_view(), name='recommendations'),
]
