from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from rest_framework.routers import SimpleRouter, DefaultRouter

router = DefaultRouter()
router.register(r'address', views.AddressViewSet)
router.register(r'review', views.ReviewViewSet)
router.register(r'', views.AuthRequestViewSet, basename='auth')

urlpatterns = [
    path('token/', obtain_auth_token, name='token'),
    path('userlist/', views.UserListView.as_view(), name='user_list'),

    path('password/reset/confirm/<str:uid>/<str:token>/',
         views.ResetPasswordConfirmView.as_view(),
         name='password_reset_confirm'),

    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

]

urlpatterns += router.urls
