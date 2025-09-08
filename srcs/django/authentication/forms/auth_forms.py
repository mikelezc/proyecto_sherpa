from django.contrib.auth.forms import UserCreationForm
from authentication.models import CustomUser
from django import forms

# Simplified user registration form for demo purposes

class RegistrationForm(UserCreationForm):
    """User registration form - simplified for demo"""

    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = True  # Simplified: activate immediately
        user.email_verified = True  # Simplified: no email verification
        if commit:
            user.save()
        return user
