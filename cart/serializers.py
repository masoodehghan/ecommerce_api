from rest_framework import serializers
from .models import Cart, CartItem


class CartSerializer(serializers.ModelSerializer):
    paying_price = serializers.DecimalField(source='get_paying_price', required=False,  read_only=True,
                                            max_digits=10, decimal_places=2)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'paying_price']


class CartItemSerializer(serializers.ModelSerializer):
    item_price = serializers.DecimalField(source='get_final_price', decimal_places=2, max_digits=10, required=False,
                                          read_only=True)
    url = serializers.URLField(source='get_absolute_url', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_price', 'url']
