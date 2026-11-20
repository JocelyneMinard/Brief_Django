from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_classes = 'w-full border border-gray-300 rounded px-3 py-2 mt-1'
        self.fields['username'].widget.attrs.update({'class': tailwind_classes})
        self.fields['password'].widget.attrs.update({'class': tailwind_classes})

