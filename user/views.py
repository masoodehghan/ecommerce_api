from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Address, AuthRequest
from .util import generate_and_send_code
from .serializers import (
    RegisterSerializer,
    AddressSerializer,
    UserSerializer,
    ReviewSerializer,
    AuthRequestSerializer,
    VerifyAuthSerializer
)

from django.contrib.auth import get_user_model
from .permissions import IsOwner
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from product.models import Product
from rest_framework.exceptions import NotAcceptable
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

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


class AuthRequestView(generics.CreateAPIView):
    serializer_class = AuthRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        response = Response(serializer.data, status.HTTP_201_CREATED)

        response.set_cookie('_req_id_',
                            serializer.data['request_id'],
                            600,
                            httponly=True,
                            )

        return response

    def perform_create(self, serializer):
        if serializer.validated_data['request_method'] == 'sms':
            code = generate_and_send_code(serializer.validated_data['receiver'])
            serializer.save(pass_code=code)

        else:
            serializer.save()


class AuthRequestVerifyView(generics.GenericAPIView):
    """
    users can login with either password or code that sms to user
    """

    serializer_class = VerifyAuthSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context=self.get_serializer_context()
        )

        serializer.is_valid(raise_exception=True)

        mobile = serializer.instance.receiver

        if serializer.instance.request_method == 'sms':
            user, created = self._login_register_sms(mobile)

        else:
            user, created = self._login_register_using_password(mobile, request.data['user_key'])

        token = get_object_or_404(Token, user=user)
        self._delete_auth_request(serializer.validated_data['request_id'])

        return Response({'token': token.key, 'created': created}, status.HTTP_200_OK)

    @staticmethod
    def _login_register_sms(mobile):
        user, created = User.objects.get_or_create(username=mobile)

        return user, created

    @staticmethod
    def _login_register_using_password(mobile, password):
        user = authenticate(username=mobile, password=password)
        created = False

        if user is None:
            user = User.objects.create_user(username=mobile, password=password)

            created = True

        return user, created

    @staticmethod
    def _delete_auth_request(req_id):
        AuthRequest.objects.filter(request_id=req_id).delete()


class ResendCodeView(generics.GenericAPIView):
    serializer_class = AuthRequestSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        request_id = self.request.COOKIES.get('_req_id_')
        obj = get_object_or_404(AuthRequest, request_id=request_id)
        return obj

    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = AuthRequestSerializer(
            instance=obj,
            data={'receiver': obj.receiver},
            context=self.get_serializer_context(),
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        receiver = serializer.validated_data['receiver']

        auth_request = AuthRequest.objects.filter(
            receiver=receiver,
            created__lt=timezone.now() - timedelta(minutes=2)
        )

        if auth_request:
            code = generate_and_send_code(receiver)
            serializer.save(pass_code=code)

            return Response(serializer.data, status.HTTP_200_OK)

        else:
            raise NotAcceptable('you have to wait 2 minutes to resend code')
