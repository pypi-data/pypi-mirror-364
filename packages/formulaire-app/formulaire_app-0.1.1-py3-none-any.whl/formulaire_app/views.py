
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, RegisterForm
from .models import Profile
from django.contrib.auth.models import User




def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(request,
                            username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
        if user:
            login(request, user)
            return redirect('login')  # Ou une page d’accueil
    return render(request, 'formulaire_app/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, date_naissance=form.cleaned_data['date_naissance'])
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'formulaire_app/register.html', {'form': form})

def forgot_password_view(request):
    return render(request, 'formulaire_app/forgot_password.html')
