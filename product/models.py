from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.conf import settings
from django.urls import reverse


def product_image_path(instance, filename):
    return f"product/images/{instance.name}/{filename}"


class Category(MPTTModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True, max_length=100)
    parent = TreeForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Product(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='user_product', on_delete=models.CASCADE, blank=True
    )
    name = models.CharField(max_length=250)
    image = models.ImageField(default='default.jpg', blank=True, upload_to=product_image_path)
    category = TreeForeignKey(Category, related_name='product_category', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=250, null=True, blank=True, unique=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    views = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductView(models.Model):
    product = models.ForeignKey(Product, blank=True, on_delete=models.CASCADE)
    ip = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.product.name
