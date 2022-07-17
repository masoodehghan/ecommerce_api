from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Address

from .serializers import (
    RegisterSerializer,
    AddressSerializer,
    UserSerializer,
    ReviewSerializer
)

from django.contrib.auth import get_user_model
from .permissions import IsOwner
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from product.models import Product
from rest_framework.exceptions import NotAcceptable

User = get_user_model()


class UserCreateView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permissions = [permissions.AllowAny]

    queryset = User.objects.prefetch_related('groups').all()


class ProfileView(generics.RetrieveAPIView, generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsOwner]
    queryset = User.objects.prefetch_related('address').all()

    lookup_field = None

    def get_object(self):
        queryset = self.get_queryset()

        obj = queryset.get(id=self.request.user.id)

        self.check_object_permissions(self.request, obj)
        return obj


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        request.user.auth_token.delete()

        return Response("you Logged out successfully.", status=200)


class AddressCreateView(generics.CreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsOwner]
    queryset = Address.objects.all()


class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product = get_object_or_404(Product, pk=self.request.data['product'])

        if product.seller == self.request.user:
            raise NotAcceptable('you cant review your own product')

        return serializer.save(user=self.request.user)


class ReviewUpdateDestroy(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwner]
