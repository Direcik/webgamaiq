from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import MyUserModelUserCreationForm, MyUserModelUserChangeForm
from .models import MyUserModel

class MyUserModelAdmin(UserAdmin):
    add_form = MyUserModelUserCreationForm
    form = MyUserModelUserChangeForm
    model = MyUserModel
    list_display= ['username']
    search_fields = ['username']
admin.site.register(MyUserModel, MyUserModelAdmin)