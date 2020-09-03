from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,UserChangeForm
from django.contrib.auth.models import User
from django import forms


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AuthenticateUserForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class ResetPasswordForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['password']