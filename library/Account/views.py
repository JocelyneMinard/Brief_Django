from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from .forms import RegisterForm, EditProfileForm
from django.urls import reverse_lazy

@login_required
def profile_view(request):
    return render(request, 'Account/profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance = request.user)

    return render(request, 'Account/edit.html', {'form': form})

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'Account/register.html'
    success_url = reverse_lazy("login")