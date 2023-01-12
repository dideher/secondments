from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    # temp attributes for cas_proxy develop
    full_name = models.CharField(max_length=64, null=True, blank=False)
    short_name = models.CharField(max_length=64, null=True, blank=False)
