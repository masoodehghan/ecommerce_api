from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from product.models import Product
from django.core.validators import MinValueValidator
User = get_user_model()


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, related_name='cart_user'
    )
    total = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        cart_item = self.cart_item.iterator()
        total_price = 0
        for prod in cart_item:
            total_price += prod.product.price * prod.quantity

        return total_price


@receiver(post_save, sender=User)
def create_cart_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, blank=True, related_name='cart_item'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_item')
    quantity = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
