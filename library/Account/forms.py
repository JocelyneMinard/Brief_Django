from cuser.forms import AuthenticationForm, UserCreationForm
from django.utils.safestring import mark_safe
from .models import User
from django import forms

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_classes = 'w-full border border-gray-300 rounded px-3 py-2 mt-1'
        self.fields['email'].widget.attrs.update({'class': tailwind_classes})
        self.fields['password'].widget.attrs.update({'class': tailwind_classes})


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150, required=True, label="First name"
    )
    last_name = forms.CharField(
        max_length=150, required=True, label="Last name"
    )
    email = forms.EmailField(required=True, label="Email address")

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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