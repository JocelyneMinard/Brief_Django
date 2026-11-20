from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout
from requests import request
from .forms import RegisterForm
from Account.models import User
from django.views.generic import TemplateView, FormView

# Create your views here.
class ReadMeIndex(TemplateView):
    template_name = "ReadMe/index.html"

user = get_user_model()
user.objects.all()

class SignUp(FormView):
    model = User
    form_class = RegisterForm 
    template_name = "ReadMe/register.html"