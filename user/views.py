from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from .models import Address, AuthRequest, Review
from .util import generate_and_send_code, sensitive_post_parameters_m
from .serializers import (
    AddressSerializer,
    UserSerializer,
    ReviewSerializer,
    AuthRequestSerializer,
    VerifyAuthSerializer,
    PasswordSerializer,
    PasswordResetCompleteSerializer,
    PasswordResetSerializer,
    PasswordChangeSerializer
)

from django.contrib.auth import get_user_model
from .permissions import IsOwner
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.exceptions import NotAcceptable
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
import logging
from rest_framework.decorators import action

logger = logging.getLogger('info')
User = get_user_model()


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permissions = [AllowAny]

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
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)

        return Response({"detail": "you Logged out successfully."}, status=200)


class AddressViewSet(mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]

        else:
            permission_classes = [IsOwner]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewViewSet(mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def perform_create(self, serializer):
        product = serializer.validated_data['product']

        if product.seller_id == self.request.user.id:
            raise NotAcceptable('you cant review your own product')

        return serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]

        else:
            permission_classes = [IsOwner]

        return [permission() for permission in permission_classes]


class AuthRequestViewSet(viewsets.GenericViewSet):
    lookup_url_kwarg = ['uid', 'token']

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['login', 'resend_code']:
            return AuthRequestSerializer

        elif self.action == 'change_password':
            return PasswordChangeSerializer

        elif self.action == 'reset_password':
            return PasswordResetSerializer

        elif self.action == 'set_password':
            return PasswordSerializer

        else:
            return VerifyAuthSerializer

    @action(methods=['post'], detail=False, url_name='login',
            url_path='login', permission_classes=[AllowAny])
    def login(self, request, *args, **kwargs):
        serializer = AuthRequestSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['receiver']

        mobile_status = self._get_mobile_status(mobile, request.data.get('login_with_code'))

        if mobile_status == AuthRequest.MobileStatuses.NOT_REGISTERED:
            self._create_user(mobile)

        code = None if mobile_status == AuthRequest.MobileStatuses.PASSWORD_LOGIN \
            else generate_and_send_code(mobile)

        serializer.save(code=code, auth_status=mobile_status)

        response = Response(serializer.data, status.HTTP_201_CREATED)

        response.set_cookie('_req_id_',
                            serializer.data['request_id'],
                            600,
                            httponly=True,
                            )

        return response

    def _get_mobile_status(self, mobile, login_with_code):
        user = self._get_user(mobile)

        if user is None:
            return AuthRequest.MobileStatuses.NOT_REGISTERED

        if login_with_code:
            return AuthRequest.MobileStatuses.CODE_LOGIN

        if user and not user.password:
            user.set_unusable_password()

        if user and user.has_usable_password():
            return AuthRequest.MobileStatuses.PASSWORD_LOGIN

        else:
            raise NotAcceptable(
                'you have not set your password you can login using verification code')

    @staticmethod
    def _get_user(mobile):
        try:
            return User.objects.get(username=mobile)
        except User.DoesNotExist:
            return None

    @staticmethod
    def _create_user(mobile):
        User.objects.create_user(username=mobile)

    def get_object(self):
        request_id = self.request.COOKIES.get('_req_id_')
        obj = get_object_or_404(AuthRequest, request_id=request_id)
        return obj

    @action(methods=['post'], detail=False, url_name='verify_login',
            url_path='login/verify', permission_classes=[AllowAny])
    def login_verify(self, request, *args, **kwargs):
        serializer = VerifyAuthSerializer(
            data=request.data, context=self.get_serializer_context()
        )

        serializer.is_valid(raise_exception=True)

        user = User.objects.get(username=serializer.instance.receiver)
        login(request, user)
        print('user: ', user)
        token = Token.objects.get(user=user)

        self._delete_auth_request(serializer.data['request_id'])

        return Response({'token': token.key}, status.HTTP_200_OK)

    @staticmethod
    def _delete_auth_request(req_id):
        AuthRequest.objects.filter(request_id=req_id).delete()

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated], url_path="password/set")
    def set_password(self, request, *args, **kwargs):
        user = self.request.user
        if user.has_usable_password():
            raise NotAcceptable('you have set your password')

        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data['password'])
        user.save()

        return Response({'message': 'password set.'}, status.HTTP_200_OK)

    @action(methods=['patch'], detail=False, permission_classes=[AllowAny])
    def resend_code(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.auth_status == AuthRequest.MobileStatuses.PASSWORD_LOGIN:
            raise NotAcceptable('you cant do this action')

        serializer = AuthRequestSerializer(
            instance=obj,
            data={'receiver': obj.receiver},
            context=self.get_serializer_context(),
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        receiver = obj.receiver

        auth_request = AuthRequest.objects.filter(
            Q(receiver=receiver) &
            Q(created__lt=timezone.now() - timedelta(minutes=2)) &
            Q(request_id=obj.request_id)
        )

        if auth_request.exists():
            code = generate_and_send_code(receiver)
            serializer.save(code=code)

            return Response(serializer.data, status.HTTP_200_OK)

        else:
            raise NotAcceptable('you have to wait 2 minutes to resend code')

    @action(['POST'], detail=False, url_path='password/reset', permission_classes=[AllowAny])
    def reset_password(self, request):
        serializer = PasswordResetSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'detail': 'password reset email sent to you.'}, status.HTTP_200_OK)

    @action(['POST'], detail=False, url_path='password/change')
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response({'detail': 'password changed successfully'}, status.HTTP_200_OK)


class ResetPasswordConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetCompleteSerializer
    permission_classes = [AllowAny]

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({'detail': 'password change successfully'}, status.HTTP_200_OK)
