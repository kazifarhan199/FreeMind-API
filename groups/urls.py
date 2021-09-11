from django.urls import path
from . import views

urlpatterns = [
    path('', views.GroupsView.as_view(), name='group'),
    path('members/', views.GroupsMemberView.as_view(), name='group-members'),
]
