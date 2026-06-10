from django.urls import path
from . import views

urlpatterns = [
    # ------------------------------------------------------------------------------------
    # Account Authentication Lifecycle Routes
    # ------------------------------------------------------------------------------------
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ------------------------------------------------------------------------------------
    # User Profile Settings Framework Panel Routes
    # ------------------------------------------------------------------------------------
    path("profile/", views.profile_view, name="profile"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path('profile_patient/', views.patient_profile, name='profile-patient'),
    
    # ------------------------------------------------------------------------------------
    # Role-Based Dashboard Workspace Shell Render Views
    # ------------------------------------------------------------------------------------
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('therapist-dashboard/', views.therapist_dashboard, name='therapist_dashboard'),
    path('profile_admin/', views.admin_profile, name='profile-admin'),
    path('about-us/', views.about_us, name='about_Us'),

    # ------------------------------------------------------------------------------------
    # Asynchronous REST DRF Administrative Users Control API
    # ------------------------------------------------------------------------------------
    path('api/admin/dashboard/', views.admin_telemetry_stats, name='admin_telemetry_stats'),
    path('api/admin/users/', views.admin_list_users, name='admin_list_users'),
    path('api/admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('api/admin/users/<int:user_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('api/admin/users/<int:user_id>/role/', views.admin_reassign_role, name='admin_reassign_role'),
    path('api/admin/users/<int:user_id>/verify/', views.admin_verify_therapist, name='admin_verify_therapist'),
    
    # ------------------------------------------------------------------------------------
    # Asynchronous REST DRF Administrative PsychoeducationArticle CRUD API
    # ------------------------------------------------------------------------------------
    path('api/admin/articles/', views.admin_list_articles, name='admin_list_articles'),
    path('api/admin/articles/<int:article_id>/', views.admin_article_detail, name='admin_article_detail'),
    path('api/admin/articles/create/', views.admin_create_article, name='admin_create_article'),
    path('api/admin/articles/<int:article_id>/edit/', views.admin_edit_article, name='admin_edit_article'),
    path('api/admin/articles/<int:article_id>/publish/', views.admin_publish_article, name='admin_publish_article'),

    #--------------url for home--------------------------------------
    path("",views.Home,name='home'),
    path("about/",views.about,name='about'),
    path("therapist/",views.Therapist_Home,name='therapist_home'),

]