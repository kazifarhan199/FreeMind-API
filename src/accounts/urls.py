from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('edit/', views.Edit.as_view(), name='edit'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('reset/', views.PasswordReset.as_view(), name='reset'),
    path('devices/', views.Devices.as_view(), name='devices'),
]
