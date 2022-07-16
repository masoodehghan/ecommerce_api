from django.db import models
from django.contrib.auth import get_user_model
from cart.models import Cart
from user.models import Address
from datetime import timedelta, date
from string import digits
from random import choice
from django.core.validators import MinValueValidator
from ecommerce.utils import TimeStampModel

User = get_user_model()


def generate_order_number(size=10):
    return ''.join(choice(digits) for _ in range(size))


class Order(TimeStampModel):
    PENDING_STATE = 'p'
    SHIPPING_STATE = 's'
    COMPLETED_STATE = 'c'

    STATUS_CHOICES = ((PENDING_STATE, 'pending'),
                      (SHIPPING_STATE, 'shipping'),
                      (COMPLETED_STATE, 'completed')
                      )

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', blank=True)
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name='order', blank=True
    )
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING_STATE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, blank=True)
    delivery_date = models.DateField(default=date.today() + timedelta(days=4),
                                     validators=[MinValueValidator(date.today() + timedelta(days=3))])

    order_number = models.CharField(
        max_length=10,
        default=generate_order_number,
        unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True,
                                      validators=[MinValueValidator(0)])
