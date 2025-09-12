from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm

class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm

# Create your views here.   
def login_view(request):
    return render(request, 'login/login.html')

