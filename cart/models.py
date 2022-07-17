from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from product.models import Product
from django.urls import reverse
from ecommerce.utils import TimeStampModel
from rest_framework.exceptions import NotAcceptable
from django.core.validators import MinValueValidator

User = get_user_model()


class Cart(TimeStampModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, related_name='cart_user'
    )

    def get_total_item(self):
        return self.cart_item.count()

    def get_paying_price(self):
        cart_item = self.cart_item.iterator()
        paying_price = 0
        for item in cart_item:
            paying_price += item.get_final_price
        return float(paying_price)

    def clear_items(self):
        self.cart_item.all().delete()


@receiver(post_save, sender=User)
def create_cart_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)


class CartItem(TimeStampModel):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, blank=True, related_name='cart_item'
    )

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_item'
    )

    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    def get_item_price(self):
        product = self.product
        return product.price * self.quantity

    def get_item_discount(self):
        product = self.product
        return product.discount_price * self.quantity

    @property
    def get_final_price(self):
        res = self.get_item_price() - self.get_item_discount()
        if res <= 0:
            raise NotAcceptable('discount cant be negative')

        return res

    def get_absolute_url(self):
        return reverse('cart:cart_item-detail', kwargs={'pk': self.pk})
