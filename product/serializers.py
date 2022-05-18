from rest_framework import serializers
from .models import Product, Category
from user.serializers import ReviewMiniSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'parent']


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude = ['modified']
        read_only_fields = ['views']


class ProductMiniSerializer(serializers.ModelSerializer):
    review = ReviewMiniSerializer(source='review_product', read_only=True, many=True)
    category = serializers.CharField(source='category.name', read_only=True)
    seller = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = Product
        exclude = ['discount_price']
        read_only_fields = ['review']
