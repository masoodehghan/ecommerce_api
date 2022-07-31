import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address, Review, AuthRequest
import django.contrib.auth.password_validation as validator
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from django.utils import timezone
from django.contrib.auth import authenticate
import logging

logger = logging.getLogger('info')
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=100, required=True, write_only=True)
    password2 = serializers.CharField(
        max_length=100, required=True, write_only=True)

    class Meta:
        model = User

        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'is_staff',
            'last_name',
            'gender', 'about',
            'password',
            'password2'
        ]

        read_only_fields = ['is_staff']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('passwords are not equal')
        data.pop('password2')
        user = User(**data)
        password = data.get('password')
        errors = dict()

        try:
            validator.validate_password(password=password, user=user)
        except ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super(RegisterSerializer, self).validate(data)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AddressSerializer(serializers.ModelSerializer):
    country = CountryField()
    url = serializers.URLField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']


class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User

        fields = ['first_name', 'last_name', 'username',
                  'email', 'gender', 'about', 'address']

        read_only_fields = ['username', 'email']


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user']


class ReviewMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ['product']


class AuthRequestSerializer(serializers.ModelSerializer):
    login_with_code = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = AuthRequest
        fields = ['request_id', 'receiver', 'auth_status', 'login_with_code']
        read_only_fields = ['request_id', 'auth_status']

    def validate_receiver(self, value):

        if not re.findall(r'^09\d{9}$', value):
            raise serializers.ValidationError('enter a valid phone number')

        return value

    def validate(self, attrs):
        attrs.pop('login_with_code', None)
        return super().validate(attrs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('receiver')
        return ret


class VerifyAuthSerializer(serializers.ModelSerializer):
    user_key = serializers.CharField(
        max_length=32, required=False, write_only=True)

    request_id = serializers.UUIDField(
        help_text='override from cookie', required=False, read_only=False
    )

    class Meta:
        model = AuthRequest
        fields = ['request_id', 'user_key', 'code']

        read_only_fields = ['code']

    def validate(self, attrs):

        req_id = self.context['request'].COOKIES.get('_req_id_')

        if req_id is None:
            raise ValidationError('request_id expired')

        attrs['request_id'] = req_id

        user_key = attrs.pop('user_key')
        self.instance = self._get_auth_request(attrs)

        if not self.auth_is_valid(self.instance, user_key):
            raise serializers.ValidationError('invalid credential.')

        return attrs

    def auth_is_valid(self, auth_request: AuthRequest, user_key):
        if auth_request.auth_status == AuthRequest.MobileStatuses.LOGIN_PASSWORD:

            return self.__validate_password(auth_request.receiver, user_key)

        else:
            return self.__validate_code(user_key, auth_request.code)

    @staticmethod
    def _get_auth_request(data: dict):
        auth_request = AuthRequest.objects.filter(**data).first()

        if auth_request is None:
            raise serializers.ValidationError('Not Found!')

        return auth_request

    def __validate_code(self, user_code, pass_code):

        if timezone.now() > self.instance.expire_time:
            raise serializers.ValidationError('your token is expired')

        return bool(user_code == pass_code)

    @staticmethod
    def __validate_password(mobile, user_key):
        return bool(authenticate(username=mobile, password=user_key))


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=64, write_only=True,
                                     style={'input_type': 'password'}, validators=[validator.validate_password])

    password2 = serializers.CharField(max_length=64, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('passwords are not match')
        return attrs

    def create(self, validated_data): pass

    def update(self, instance, validated_data): pass
