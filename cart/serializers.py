from rest_framework import serializers
from .models import Cart, CartItem


class CartSerializer(serializers.ModelSerializer):
    # total_price = serializers.IntegerField()

    class Meta:
        model = Cart
        fields = ['id', 'total', 'user', 'total_price']


class CartItemSerializer(serializers.ModelSerializer):
    cart = CartSerializer(required=False)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity']
