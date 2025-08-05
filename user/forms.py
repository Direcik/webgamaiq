from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MyUserModel

class MyUserModelUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = MyUserModel()
        fields = ('username',)

class MyUserModelUserChangeForm(UserChangeForm):
    class Meta:
        model = MyUserModel
        fields = ('username',)

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50, label="Kullanıcı Adı")
    password = forms.CharField(max_length=20, label="Parola", widget=forms.PasswordInput)
    confirm = forms.CharField(max_length=20, label="Parola Doğrula", widget=forms.PasswordInput)


class LoginForm(forms.Form):
    username = forms.CharField(label = "Kullanıcı Adı")
    password = forms.CharField(label = "Parola", widget=forms.PasswordInput)