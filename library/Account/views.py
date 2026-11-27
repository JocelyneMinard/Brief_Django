from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from .forms import RegisterForm, EditProfileForm
from django.urls import reverse_lazy

@login_required
def profile_view(request):
    """
    Display the profile page of the currently authenticated user.

    Args:
        request (HttpRequest): The HTTP request object containing the logged-in user.

    Returns:
        HttpResponse: Rendered 'Account/profile.html' template.
    """
    return render(request, 'Account/profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    """
    Handle displaying and submitting the user profile edit form.

    If the request method is POST and the form is valid, saves the updated user
    details and redirects to the profile page. Otherwise, renders the form
    pre-populated with the current user's data.

    Args:
        request (HttpRequest): The incoming HTTP request (GET or POST).

    Returns:
        HttpResponse: Redirects to 'profile' on success, or renders
            'Account/edit.html' with the form context.
    """
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance = request.user)

    return render(request, 'Account/edit.html', {'form': form})

class RegisterView(CreateView):
    """
    Generic view handling new user registration.

    Uses `RegisterForm` to create a new user account and redirects
    to the login page upon successful registration.
    """
    form_class = RegisterForm
    template_name = 'Account/register.html'
    success_url = reverse_lazy("login")