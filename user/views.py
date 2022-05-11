from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from .permissions import IsOwner
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

User = get_user_model()


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permissions = [permissions.IsAdminUser]

    queryset = User.objects.all()


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsOwner]
    queryset = User.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        request.user.auth_token.delete()

        return Response("you Logged out successfully.", status=200)


