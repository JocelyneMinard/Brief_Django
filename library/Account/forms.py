from cuser.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.utils.safestring import mark_safe
from .models import User
from django import forms

class CustomLoginForm(AuthenticationForm):
    """
    Custom authentication form using email and password with Tailwind CSS styling.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the form with French labels and Tailwind CSS widget classes.

        Args:
            *args: Variable length argument list passed to AuthenticationForm.
            **kwargs: Arbitrary keyword arguments passed to AuthenticationForm.
        """
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "Adresse e-mail"
        self.fields['password'].label = "Mot de passe"

        tailwind_classes = 'w-full border border-gray-300 rounded px-3 py-2 mt-1'
        self.fields['email'].widget.attrs.update({'class': tailwind_classes})
        self.fields['password'].widget.attrs.update({'class': tailwind_classes})


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150, required=True, label="Prénom"
    )
    last_name = forms.CharField(
        max_length=150, required=True, label="Nom"
    )
    email = forms.EmailField(required=True, label="Adresse e-mail")
  
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = "Mot de passe"
        self.fields['password2'].label = "Confirmation du mot de passe"

        tailwind_classes = 'w-full border border-gray-300 rounded px-3 py-2 mt-1'
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': tailwind_classes})
            if field.help_text and '<ul>' in str(field.help_text):
                field.help_text = mark_safe(
                    str(field.help_text).replace('<ul>', '<ul class="helptext">')
                )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
        return user

class EditProfileForm(UserChangeForm):
    """
    Form allowing authenticated users to update their basic profile information
    (email, first name, and last name) without exposing the password field.
    """
    password = None

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        """
        Initialize the form fields with Tailwind CSS styling.

        Args:
            *args: Variable length argument list passed to UserChangeForm.
            **kwargs: Arbitrary keyword arguments passed to UserChangeForm.
        """
        super().__init__(*args, **kwargs)
        tailwind_classes = 'w-full border border-gray-300 rounded px-3 py-2 mt-1'
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': tailwind_classes})