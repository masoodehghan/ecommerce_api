from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

router.register(r'address', views.AddressViewSet)
router.register(r'review', views.ReviewViewSet)


urlpatterns = [
    path('token/', obtain_auth_token, name='token'),
    # path('register/', views.UserCreateView.as_view(), name='register'),
    path('userlist/', views.UserListView.as_view(), name='user_list'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('set-password/', views.SetPasswordView.as_view(), name='set_password'),
    path('login/', views.AuthRequestView.as_view(), name='login'),
    path('login/verify/', views.AuthRequestVerifyView.as_view(), name='verify-login'),
    path('resend-code/', views.ResendCodeView.as_view(), name='resend-code')

]

urlpatterns += router.urls
