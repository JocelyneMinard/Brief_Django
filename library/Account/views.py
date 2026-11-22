from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import CreateView
from .forms import RegisterForm
from django.urls import reverse_lazy

@login_required
def profile_view(request):
    return render(request, 'Account/profile.html', {'user': request.user})


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'Account/register.html'
    success_url = reverse_lazy("login")