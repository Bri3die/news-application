from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    # Web views
    path('', views.home, name='home'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='news/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # Editor views
    path('editor/', views.editor_dashboard, name='editor_dashboard'),
    path('editor/approve/<int:pk>/', views.approve_article, name='approve_article'),
    path('editor/preview/<int:pk>/', views.editor_preview_article, name='editor_preview_article'),

    # Journalist views
    path('journalist/', views.journalist_dashboard, name='journalist_dashboard'),
    path('journalist/article/create/', views.create_article, name='create_article'),
    path('journalist/article/<int:pk>/edit/', views.edit_article, name='edit_article'),
    path('journalist/article/<int:pk>/delete/', views.delete_article, name='delete_article_web'),
    path('journalist/newsletter/create/', views.create_newsletter, name='create_newsletter'),
    path('journalist/newsletter/<int:pk>/edit/', views.edit_newsletter, name='edit_newsletter'),
    path('journalist/newsletter/<int:pk>/delete/', views.delete_newsletter, name='delete_newsletter'),

    # Subscription views
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('subscriptions/publisher/<int:pk>/', views.toggle_publisher_subscription,
         name='toggle_publisher_subscription'),
    path('subscriptions/journalist/<int:pk>/', views.toggle_journalist_subscription,
         name='toggle_journalist_subscription'),

    # Newsletter views
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path('newsletters/<int:pk>/', views.newsletter_detail, name='newsletter_detail'),

    # API endpoints
    path('api/token/', obtain_auth_token, name='api_token'),
    path('api/articles/', views.article_list_create, name='api_articles'),
    path('api/articles/subscribed/', views.subscribed_articles, name='api_subscribed_articles'),
    path('api/articles/<int:pk>/', views.article_detail_api, name='api_article_detail'),
    path('api/newsletters/', views.newsletter_list_create, name='api_newsletters'),
    path('api/newsletters/<int:pk>/', views.newsletter_detail_api, name='api_newsletter_detail'),
]