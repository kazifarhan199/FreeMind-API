from django.urls import path, include
from . import views 

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notifications'),
    path('how-many/', views.NotificationHowMany.as_view(), name='notifications-how-many'),
]
