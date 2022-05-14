from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator
from rest_framework.authentication import TokenAuthentication


class User(AbstractUser):
    GENDER_CHOICES = (('m', 'male'),
                      ('f', 'female'),
                      ('o', 'other')
                      )

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    # TODO: add phone number field
    about = models.TextField(default='', max_length=400, blank=True)

    def __str__(self):
        return self.username

    # TODO: add online function


class Address(models.Model):
    country = CountryField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address', blank=True)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    building_number = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    apartment_number = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.user.username


class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'
