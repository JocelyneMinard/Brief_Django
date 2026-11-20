from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User
from django import forms
from django.contrib.auth import logout

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_classes = 'w-full border border-gray-300 rounded px-3 py-2 mt-1'
        self.fields['username'].widget.attrs.update({'class': tailwind_classes})
        self.fields['password'].widget.attrs.update({'class': tailwind_classes})

def logout_view(request):
    logout(request)


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_classes = 'w-full border border-gray-300 rounded px-3 py-2 mt-1'
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': tailwind_classes})

    first_name = forms.CharField(
        max_length=150, required=True, label="First name"
    )
    last_name = forms.CharField(
        max_length=150, required=True, label="Last name")
    email = forms.EmailField(required=True, label="Email adress")

    class Meta:
        model = User
        fields = ("username", "first_name","last_name","email")

    def save_user(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
        return user 