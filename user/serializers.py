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
        fields = ['request_id', 'receiver', 'request_method', 'pass_code']
        read_only_fields = ['request_id', 'pass_code']

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
        fields = ['request_id', 'user_code', 'pass_code']

        extra_kwargs = {'request_id': {'read_only': False, 'required': False}}

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
    def _delete_auth_request(id):
        AuthRequest.objects.filter(request_id=id).delete()

    def create(self, validated_data): pass

    def to_representation(self, instance):

        if self.instance.request_method == 'email':

            user_email = instance.receiver

            user, created = User.objects.get_or_create(
                username=user_email.split('@')[0], email=user_email
            )

            logger.info(user)
            token = Token.objects.get(user=user)

        self._delete_auth_request(instance.request_id)

        return {
            'created': created,
            'token': token.key
        }
