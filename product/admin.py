from django.contrib import admin
from .models import Category, Product


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ['views', 'slug']


admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
