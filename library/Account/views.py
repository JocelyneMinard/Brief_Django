from django.contrib.auth import get_user_model
from django.views.generic import CreateView
from .forms import RegisterForm
from django.urls import reverse_lazy

# Create your views here.
user = get_user_model()
user.objects.all()

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'Account/register.html'
    success_url = reverse_lazy("login")