from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    # Здесь можно добавить дополнительные поля в будущем
    pass
