from django.urls import include, path
from django.contrib.auth import views as auth_views
from .forms import CustomLoginForm, EditProfileForm
from .views import RegisterView
from . import views

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name = 'Account/login.html',
            authentication_form = CustomLoginForm,
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit/', views.edit_profile_view, name='edit'),
    path('register/', RegisterView.as_view(), name='register'),
]