from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout, authenticate, login
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib import messages
from catalog.models import Customer
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm, UserProfileForm

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'users/profile.html')

@require_POST
def logout_view(request):
    logout(request)
    return redirect('catalog:product_list')

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('catalog:product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})
