from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import NotAcceptable, ValidationError
from .serializers import CartItemSerializer
from .models import CartItem, Cart
from product.models import Product
from .permissions import IsCartOwner
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK


class CartItemListCreate(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return CartItem.objects.filter(cart__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        product = get_object_or_404(Product, pk=self.request.data['product'])
        cart = get_object_or_404(Cart, user=user)
        current_item = CartItem.objects.filter(cart=cart, product=product)

        if user == product.seller:
            raise NotAcceptable('this is your own product')

        if current_item.count() > 0:
            raise NotAcceptable('you already have this product in cart')

        try:
            quantity = int(self.request.data['quantity'])
        except Exception as e:
            raise ValidationError("Enter Valid Quantity")

        if quantity > product.quantity:
            raise NotAcceptable('you order quantity is more than product quantity available')
        serializer.save(cart=cart, product=product, quantity=quantity)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsCartOwner]

    def get_queryset(self):
        user = self.request.user
        return CartItem.objects.filter(cart__user=user)

    def perform_update(self, serializer):
        product = get_object_or_404(Product, pk=self.request.data.get('product'))
        cart = get_object_or_404(Cart, user=self.request.user)
        current_item = CartItem.objects.filter(cart=cart, product=product)

        if current_item.count() > 0:
            raise NotAcceptable('you already have this product in cart')

        try:
            quantity = int(self.request.data['quantity'])
        except Exception:
            raise ValidationError("Enter Valid Quantity")

        if quantity > product.quantity:
            raise NotAcceptable('you order quantity is more than product quantity available')

        serializer.is_valid(raise_exception=True)
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


