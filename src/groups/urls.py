from django.urls import path
from . import views

urlpatterns = [
    path('', views.GroupsView.as_view(), name='group'),
    path('create/', views.GroupsCreateView.as_view(), name='group-create'),
    path('members/', views.GroupsMemberView.as_view(), name='group-members'),
    path('gchannel/', views.GroupsChannelView.as_view(), name='group-channel'),
]
