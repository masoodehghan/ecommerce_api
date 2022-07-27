from django.contrib import admin

from user.models import AuthRequest, User


admin.site.register(AuthRequest)
admin.site.register(User)
