from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('user.urls')),
    path('api/', include('product.urls')),
    path('api/', include('cart.urls')),
    path('api/', include('order.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework'))
]

urlpatterns += static(settings.MEDIA_ROOT, document_root=settings.MEDIA_URL)
