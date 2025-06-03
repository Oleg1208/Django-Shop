from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'users'  # добавляем определение namespace

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    # Token authentication endpoints
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('api/token/refresh/', views.refresh_token, name='api_token_refresh'),
] 