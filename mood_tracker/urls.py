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


    path('phq9/', views.phq9_assessment, name='phq9'),
    path('gad7/', views.gad7_assessment, name='gad7'),
    path('phq9/history/', views.phq9_history, name='phq9_history'),
    path('gad7/history/', views.gad7_history, name='gad7_history'),

    path('articles/recommended/', views.recommended_articles, name='recommended_articles'),


    path('mood/trend/<int:days>/', views.mood_trend, name='mood_trend'),

    path('role_redirect/', views.role_redirect, name="role_redirect"),
    



]

