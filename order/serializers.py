from rest_framework import serializers
from .models import Order
from cart.serializers import CartSerializer


class OrderSerializer(serializers.ModelSerializer):
    cart_item = CartSerializer(source='cart.cart_item', many=True, required=False)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['cart_item', 'total_price']


