from django.urls import path
from . import views

urlpatterns = [
    path('checkin/', views.mood_checkin, name='mood_checkin'),
    path('history/', views.mood_history, name='mood_history'),
    path('chart-data/', views.mood_chart_data, name='mood_chart_data'),


    
    path('journal/', views.journal_list, name='journal_list'),
    path('journal/create/', views.journal_create, name='journal_create'),
    path('journal/<int:pk>/update/', views.journal_update, name='journal_update'),
    path('journal/<int:pk>/delete/', views.journal_delete, name='journal_delete'),


    
    path('articles/', views.article_list, name='article_list'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),



    

    

]

