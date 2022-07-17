from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator
from rest_framework.authentication import TokenAuthentication
from product.models import Product
from ecommerce.utils import TimeStampModel


class User(AbstractUser):
    GENDER_CHOICES = (('m', 'male'),
                      ('f', 'female'),
                      ('n', 'non-binary')
                      )

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    # TODO: add phone number field
    about = models.TextField(default='', max_length=400, blank=True)

    def __str__(self):
        return self.username

    # TODO: add online function


class Address(models.Model):
    country = CountryField()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='address',
        blank=True)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    building_number = models.IntegerField(
        blank=True, null=True, validators=[
            MinValueValidator(1)])
    apartment_number = models.IntegerField(
        blank=True, null=True, validators=[
            MinValueValidator(1)])
    primary = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("address-detail", kwargs={"pk": self.pk})



class Review(TimeStampModel):
    REVIEW_CHOICES = (('u', 'Up Value'),
                      ('d', 'Down Value'),
                      ('o', 'Not Sure')
                      )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        related_name='review_user')
    pros = models.CharField(max_length=100, default='')
    cons = models.CharField(max_length=100, default='')
    content = models.CharField(max_length=100, default='')
    value = models.CharField(max_length=1, choices=REVIEW_CHOICES)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='review_product')

    class Meta:
        unique_together = ['product', 'user']


class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'
