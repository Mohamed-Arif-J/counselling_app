from django.urls import path
from . import views

urlpatterns = [
    path('checkin/', views.mood_checkin, name='mood_checkin'),
    path('history/', views.mood_history, name='mood_history'),
    path('chart-data/', views.mood_chart_data, name='mood_chart_data')
    

]

