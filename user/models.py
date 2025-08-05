from django.db import models
from django.contrib.auth.models import AbstractUser

class MyUserModel(AbstractUser):
    def __str__(self):
        return self.username