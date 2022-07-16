from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views


urlpatterns = [
    path('login', obtain_auth_token, name='login'),
    path('register', views.UserCreateView.as_view(), name='register'),
    path('userlist', views.UserListView.as_view(), name='user_list'),
    path('profile', views.ProfileView.as_view(), name='profile'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('address/create', views.AddressCreateView.as_view(), name='address-create'),
    path('address/<int:pk>/', views.AddressRetrieveView.as_view(), name='address-detail'),
    path('review', views.ReviewCreate.as_view(), name='review_create'),
    path('review/<int:pk>/', views.ReviewUpdateDestroy.as_view(), name='review_detail')
]
