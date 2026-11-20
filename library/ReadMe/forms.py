from django import forms


class RegisterForm(UserCreationForm):
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