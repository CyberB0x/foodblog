from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full p-2 border rounded',
        'placeholder': 'Username'
    }))

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full p-2 border rounded',
        'placeholder': 'Email'
    }))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border rounded pr-10',
        'placeholder': 'Password',
        'id': 'password1'
    }))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border rounded pr-10',
        'placeholder': 'Confirm Password',
        'id': 'password2'
    }))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.help_text = None
            field.label = ""