from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    GENDER_CHOICES = (('m', 'male'),
                      ('f', 'female'),
                      ('o', 'other')
                      )

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    description = models.TextField(default='', max_length=400, blank=True)
