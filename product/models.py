from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.conf import settings
from django.core.validators import MinValueValidator
from ecommerce.utils import TimeStampModel


class CategoryManager(models.Manager):

    def parent_to_root(self, category):
        if category.parent is None:
            return [category]

        else:
            return self.parent_to_root(category.parent) + [category]

    def get_children(self, category):
        children = []
        for child in category.get_sub_categories():
            children.append(child)
            children.extend(self.get_children(child))

        return children

    def get_root_categories(self):
        return self.filter(parent=None)


class Category(TimeStampModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True, max_length=100)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children')

    objects = CategoryManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

    def get_sub_categories(self):
        return self.children.all()


def product_image_path(instance, filename):
    return f"product/images/{instance.name}-{filename}"


class Product(TimeStampModel):

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='user_product', on_delete=models.CASCADE, blank=True
    )

    image = models.ImageField(
        default='default.jpg',
        upload_to=product_image_path)

    name = models.CharField(max_length=250)

    category = models.ForeignKey(
        Category, related_name='product_category', on_delete=models.CASCADE
    )

    slug = models.SlugField(max_length=250, null=True, blank=True, unique=True)
    quantity = models.IntegerField(default=1)

    price = models.DecimalField(
        decimal_places=2, max_digits=10, validators=[MinValueValidator(0)]
    )

    description = models.TextField(null=True, blank=True)
    views = models.IntegerField(default=0)

    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, blank=True,
        validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name


class ProductView(TimeStampModel):
    product = models.ForeignKey(Product, blank=True, on_delete=models.CASCADE)
    ip = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.product.name
