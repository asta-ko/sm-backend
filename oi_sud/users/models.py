from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class CustomUser(AbstractUser):
    regions = ArrayField(models.IntegerField(blank=True, null=True), verbose_name='Регионы', blank=True, null=True)
    favorite_cases = models.ManyToManyField('cases.Case', related_name='favorited_users', blank=True)

    def __str__(self):
        return self.email


class UserTag(models.Model):
    cases = models.ManyToManyField('cases.Case', related_name='user_tags', blank=True)
    user = models.ForeignKey(CustomUser, related_name='tags', on_delete=models.CASCADE, blank=True, null=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
