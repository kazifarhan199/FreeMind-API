from django.urls import path, include
from . import views 


urlpatterns = [
    path('stress/', views.collect_garmin_stress_data_view, name='stress'),
    path('daily/', views.collect_garmin_daily_data_view, name='daily'),
    path('sleep/', views.collect_garmin_sleep_data_view, name='sleep')
]
