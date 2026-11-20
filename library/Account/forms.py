from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_classes = 'w-full border border-gray-300 rounded px-3 py-2 mt-1'
        self.fields['username'].widget.attrs.update({'class': tailwind_classes})
        self.fields['password'].widget.attrs.update({'class': tailwind_classes})

def logout_view(request):
    logout(request)