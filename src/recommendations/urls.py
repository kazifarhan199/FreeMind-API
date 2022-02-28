from django.urls import path, include
from . import views 

urlpatterns = [
    path('', views.LabelsListView.as_view(), name='labels'),
    path('label-create/', views.LabelsCreateView.as_view(), name='labels-create'),
    path('rating/', views.RecommendationsView.as_view(), name='recommendations'),
]
