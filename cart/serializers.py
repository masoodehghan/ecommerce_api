from django.shortcuts import get_object_or_404
from rest_framework import serializers

from product.models import Product
from .models import Cart, CartItem


class CartSerializer(serializers.ModelSerializer):

    paying_price = serializers.DecimalField(
        source='get_paying_price',
        read_only=True,
        max_digits=10,
        decimal_places=2)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'paying_price']


class CartItemSerializer(serializers.ModelSerializer):
    item_price = serializers.DecimalField(
        source='get_final_price',
        decimal_places=2,
        max_digits=10,
        required=False,
        read_only=True
    )

    url = serializers.URLField(source='get_absolute_url', read_only=True)

    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'item_price', 'url']

    def validate(self, data):
        user = self.context['request'].user
        product = data['product']

        cart = get_object_or_404(Cart, user=user)

        current_item = CartItem.objects.filter(cart=cart, product=product)

        if user == product.seller:
            raise serializers.ValidationError('this is your own product')

        if self.context['request'].method == 'POST':
            if current_item.count() > 0:
                raise serializers.ValidationError(
                    'you already have this product in cart')

        if data['quantity'] > product.quantity:
            raise serializers.ValidationError(
                'you order quantity is more than product quantity available')

        data['cart'] = cart

        return data

    def create(self, validated_data):
        print(validated_data)
        return super().create(validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['product'] = instance.product.name

        return ret


class CartItemMiniSerializer(serializers.ModelSerializer):
    item_price = serializers.DecimalField(
        source='get_final_price',
        decimal_places=2,
        max_digits=10,
        required=False,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_price']
        read_only_fields = ['product']
