from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from .forms import CustomLoginForm

urlpatterns = [
    path("", include("ReadMe.urls")),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name = 'Account/login.html',
            authentication_form = CustomLoginForm,
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]