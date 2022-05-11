from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(max_length=100, required=True, write_only=True)
    password2 = serializers.CharField(max_length=100, required=True, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'is_staff', 'last_name',
                  'gender', 'about', 'password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('passwords are not equal')
        data.pop('password2')
        return data

    def create(self, validated_data):
        password = validated_data.get('password1')  # get password from validated data
        validated_data.pop('password1')  # don't need password1 anymore
        return User.objects.create_user(password=password, **validated_data)
