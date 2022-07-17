from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order
from cart.models import Cart, CartItem
from user.models import Address
from cart.serializers import CartItemMiniSerializer
from user.serializers import AddressSerializer
from rest_framework.exceptions import NotAcceptable
from .serializers import OrderSerializer


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        if not user.address.exists():
            raise NotAcceptable('you dont have any address')

        if not cart.cart_item.exists():
            raise NotAcceptable('you dont have any item in cart')

        address = Address.objects.filter(user=user).first()
        delivery_fee = 20.0

        total_price = cart.get_paying_price() + delivery_fee
        cart_items = CartItem.objects.select_related(
            'product').filter(cart=cart)
        data = dict()
        data['address'] = AddressSerializer(address, many=False).data
        data['paying_price'] = total_price
        data['items'] = CartItemMiniSerializer(cart_items, many=True).data

        return Response(data, status=200)


class OrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)

        if not cart.cart_item.exists():
            raise NotAcceptable('you dont have any item in cart')

        address = Address.objects.filter(user=user, primary=True).first()

        if address is None:
            raise NotAcceptable('you dont have any primary address')

        for item in cart.cart_item.iterator():
            if item.product.quantity == 0:
                raise NotAcceptable('no product in stock for you')

        delivery_fee = 20.0
        total_price = cart.get_paying_price() + delivery_fee

        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(cart=cart, address=address, buyer=user, total_price=total_price)

        return Response(serializer.data, status=201)


class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)
