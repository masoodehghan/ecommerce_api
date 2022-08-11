from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r'category', views.CategoryViewSet)


urlpatterns = [
    path(
        'products/',
        views.ProductList.as_view(),
        name='product-list'
    ),

    path(
        'products/<str:slug>/',
        views.ProductDetail.as_view(),
        name='product-detail'
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

urlpatterns += router.urls
