from .serializers import (
    ProductSerializer, CategorySerializer, ProductMiniSerializer
)
from .models import Product, Category, ProductView
from rest_framework import permissions, generics, filters
from .permissions import IsSeller
from django.shortcuts import get_object_or_404


class ProductList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['name', 'seller', 'category__name']
    ordering_fields = ['views', 'price', 'created']

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'seller')

        fields = ['name', 'price', 'category__name', 'created',
                  'discount_price', 'seller__username', 'views',
                  'description', 'quantity', 'slug', 'image'
                  ]

        return queryset.only(*fields)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSeller]
    queryset = Product.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductMiniSerializer
        else:
            return ProductSerializer

    def get(self, request, *args, **kwargs):
        self._add_views_to_product()
        return self.retrieve(request, *args, **kwargs)

    def _add_views_to_product(self):
        product = self.get_object()

        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        if not ProductView.objects.filter(ip=ip, product=product).exists():
            ProductView.objects.create(product=product, ip=ip)
            product.views += 1
            product.save()


class CategoryListCreate(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_serializer(self, *args, **kwargs):

        kwargs['fields'] = {'id', 'slug', 'name'}
        return super().get_serializer(*args, **kwargs)

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]


class ProductListByCategory(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price']

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(category=category)


class CategoryDetail(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'
    queryset = Category.objects.all()
