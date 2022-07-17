from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .serializers import CartItemSerializer
from .models import CartItem, Cart
from .permissions import IsCartOwner


class CartItemListCreate(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user

        fields = ['cart', 'product__name', 'quantity',
                  'product__discount_price', 'product__price']

        return CartItem.objects.select_related(
            'product').filter(cart__user=user).only(*fields)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsCartOwner]

    def get_queryset(self):
        user = self.request.user
        return CartItem.objects.filter(cart__user=user)
