from rest_framework import serializers
from .models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'parent']


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude = ['modified']
        read_only_fields = ['views']


