from rest_framework import serializers
from .models import Product, Category
from user.serializers import ReviewMiniSerializer


class CategoryChildSerializer(serializers.ModelSerializer):
    childrens = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'childrens']

    def get_childrens(self, obj):
        max_depth = self.context.get('max_depth', -1) - 1

        if max_depth == 0:
            return []

        context = {'max_depth': max_depth}

        return CategoryChildSerializer(
            obj.children, many=True, context=context).data


class CategoryParentSerializer(serializers.ModelSerializer):
    # parent_to_root = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name']

    # def get_parent_to_root(self, obj):

    #     return CategoryParentSerializer(
    #         Category.objects.parent_to_root(obj), many=True
    #     ).data


class CategorySerializer(serializers.ModelSerializer):

    parent_to_root = serializers.SerializerMethodField(read_only=True)

    childrens = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category

        fields = ['id', 'slug', 'name', 'parent',
                  'childrens', 'parent_to_root']

        read_only_fields = ['slug']

    def get_childrens(self, obj):
        max_depth = self.context.get('max_depth', -1) - 1

        if max_depth == 0:
            return []

        context = {'max_depth': max_depth}

        return CategoryChildSerializer(
            obj.children, many=True, context=context).data

    def get_parent_to_root(self, obj):
        parents = []
        parent = obj.parent

        while parent:
            parents.append(parent)
            parent = parent.parent

        return CategoryParentSerializer(parents, many=True).data


class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.CharField(source='seller.username', read_only=True)

    category_name = serializers.CharField(
        source='category.name', read_only=True)

    class Meta:
        model = Product
        exclude = ['modified']
        extra_kwargs = {'category': {'write_only': True}}

        read_only_fields = ['views', 'seller', 'slug']

    def validate(self, data):

        if data['price'] < data['discount_price']:

            raise serializers.ValidationError(
                'Discount cant be more than Price.')

        return super().validate(data)


class ProductMiniSerializer(serializers.ModelSerializer):

    review = ReviewMiniSerializer(source='review_product',
                                  read_only=True, many=True)

    category = serializers.CharField(source='category.name', read_only=True)
    seller = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = Product
        exclude = ['discount_price']
        read_only_fields = ['review']
