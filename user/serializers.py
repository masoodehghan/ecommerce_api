from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address, Review
import django.contrib.auth.password_validation as validator
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField

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
