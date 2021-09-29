from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post'),
    path('create/', views.PostCreateView.as_view(), name='post-create'),
    path('detail/', views.PostDetailView.as_view(), name='post-detail'),
    path('delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('likes/', views.PostLikesListView.as_view(), name='post-likes'),
    path('likes/detail/', views.PostLikeView.as_view(), name='post-likes'),
    path('comments/', views.PostCommentListView.as_view(), name='post-comments'),
    path('comments/detail/', views.PostCommentView.as_view(), name='post-comments'),
]
