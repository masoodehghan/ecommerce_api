from datetime import datetime
import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address, Review, AuthRequest
import django.contrib.auth.password_validation as validator
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from django.utils import timezone
from rest_framework.authtoken.models import Token
from .util import send_email_to_user
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

    class Meta:
        model = AuthRequest
        fields = ['request_id', 'receiver', 'request_method']
        read_only_fields = ['request_id']

    def validate_receiver(self, value):

        if not re.findall(r'^09\d{9}$', value):
            raise serializers.ValidationError('enter a valid phone number')

        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        self._send_code(instance.receiver, ret.pop('pass_code'))

        return ret

    def validate(self, data):

        if data['request_method'] == 'email':
            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

            if re.fullmatch(email_regex, data['receiver']):
                return data
            else:
                raise ValidationError('email is not valid.')

        else:
            pass  # TODO: add phone number validation

    @staticmethod
    def _send_code(receiver_email, pass_code):

        # print('pass_code: ', pass_code)
        send_email_to_user(receiver_email, pass_code)


class VerifyAuthSerializer(serializers.ModelSerializer):
    user_code = serializers.CharField(
        max_length=5, required=True, write_only=True)

    class Meta:
        model = AuthRequest
        fields = ['request_id', 'user_key', 'pass_code']

        read_only_fields = ['pass_code']

    def validate(self, attrs):
        try:
            attrs['request_id'] = self.context['request'].COOKIES['request_id']

        except KeyError:
            raise ValidationError('request_id expired')

        user_code = attrs.pop('user_code')

        self.instance = self._get_auth_request(attrs)

        self.__validate_code(user_code, self.instance.pass_code)

        return attrs

    def auth_is_valid(self, auth_request: AuthRequest, user_key):
        if auth_request.request_method == 'pass':

            return self.__validate_password(auth_request.receiver, user_key)

        else:
            return self.__validate_code(user_key, auth_request.pass_code)

    @staticmethod
    def _get_auth_request(data):

        auth_request = AuthRequest.objects.filter(**data).first()

        if auth_request is None:
            raise serializers.ValidationError('Not Found!')

        return auth_request

    def __validate_code(self, user_code, pass_code):
        logger.info(self.instance.expire_time)

        if timezone.now() > self.instance.expire_time:
            raise serializers.ValidationError('your token is expired')

        elif user_code != pass_code:
            raise serializers.ValidationError('your token is incorrect')

    @staticmethod
    def __validate_password(username, user_key):
        errors = dict()
        user_is_exist = bool(authenticate(username=username, password=user_key))
        logger.info(user_is_exist)

        if not user_is_exist:
            try:
                validator.validate_password(password=user_key)

            except ValidationError as e:
                errors['password'] = list(e.messages)

            if errors:
                raise serializers.ValidationError(errors)

        return user_is_exist
