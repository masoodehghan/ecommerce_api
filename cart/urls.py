from django.urls import path
from .views import CartItemListCreate, CartItemDetailView

urlpatterns = [
    path('cart', CartItemListCreate.as_view()),
    path('cart-item/<int:pk>/', CartItemDetailView.as_view())
]
