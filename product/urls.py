from django.urls import path
from . import views


urlpatterns = [
    path(
        'products/',
        views.ProductList.as_view(),
        name='product-list'
    ),

    path(
        'products/<slug:slug>/',
        views.ProductDetail.as_view(),
        name='product-detail'
    ),

    path(
        'category/',
        views.CategoryListCreate.as_view(),
        name='category-list'
    ),

    path(
        'category/<slug:slug>/products/',
        views.ProductListByCategory.as_view(),
        name='category-prodcuts'
    ),

    path(
        'category/<slug:slug>/',
        views.CategoryDetail.as_view(),
        name='category_detail'
    )

]
