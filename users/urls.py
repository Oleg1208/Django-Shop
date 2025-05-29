from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'  # добавляем определение namespace

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
] 