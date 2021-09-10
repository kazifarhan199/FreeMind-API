from django.urls import path
from . import views

urlpatterns = [
    path('', views.GroupsView.as_view(), name='group'),
    path('members/', views.GroupsMemberView.as_view(), name='group-members'),
    # path('create/', views.CreateGroup.as_view(), name='group-create'),
    # path('edit/', views.EditGroup.as_view(), name='group-edit'),
    # path('members-add/', views.Edit.as_view(), name='members-add'),
    # path('members-remove/', views.Logout.as_view(), name='members-remove'),

    # path('no-of-groups/', views.NoOfGroups.as_view(), name='no-of-groups'),
]
