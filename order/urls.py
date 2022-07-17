from django.urls import path
from .views import CheckoutView, OrderView, OrderDetail

app_name = 'order'
urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order/', OrderView.as_view(), name='order'),
    path('order/<int:pk>/', OrderDetail.as_view())

]
