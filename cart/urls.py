from django.urls import path
from .views import CartItemListCreate, CartItemDetailView

app_name = 'cart'

urlpatterns = [
    path('cart', CartItemListCreate.as_view(), name='cart_list'),
    path('cart-item/<int:pk>/', CartItemDetailView.as_view(), name='cart_item-detail')
]
