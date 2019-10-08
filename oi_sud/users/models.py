from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models

class CustomUser(AbstractUser):

    regions = ArrayField(models.IntegerField(blank=True, null=True), verbose_name='Регионы', blank=True, null=True)
    # add additional fields in here

    def __str__(self):
        return self.email