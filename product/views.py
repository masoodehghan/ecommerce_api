from .serializers import ProductSerializer, CategorySerializer
from .models import Product, Category, ProductView
from rest_framework import permissions, generics, filters
from .permissions import IsSeller
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


class ProductList(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    queryset = Product.objects.all()
    search_fields = ['name', 'seller__username', 'category__name']

    ordering_fields = ['views', 'price', 'created']


class ProductCreate(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        category = get_object_or_404(Category, id=self.request.data.get('category'))
        serializer.save(seller=self.request.user, category=category)


class ProductUpdateDestroyView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsSeller]
    queryset = Product.objects.all()


class ProductDetail(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs.get('slug'))
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if not ProductView.objects.filter(ip=ip, product=product).exists():
            ProductView.objects.create(product=product, ip=ip)
            product.views += 1
            product.save()

        serializer = ProductSerializer(product)
        return Response(serializer.data, status=200)


class CategoryListCreate(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

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
        category = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        return Product.objects.filter(category=category)


class CategoryDetail(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'
    queryset = Category.objects.all()
