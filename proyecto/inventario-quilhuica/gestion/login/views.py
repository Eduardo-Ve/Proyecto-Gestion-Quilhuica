from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
from django.contrib.auth import login as auth_login
class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm

# Create your views here.   


def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("home")  # reemplaza con tu página principal
    else:
        form = CustomLoginForm()
    return render(request, "login/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')
