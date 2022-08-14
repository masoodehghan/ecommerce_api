from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from product.models import Category, Product

User = get_user_model()


class ProductTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test user', password='1234')

        self.category = Category.objects.create(name='test category')

        self.product = Product.objects.create(
            name='test', price=100, seller_id=1, category_id=1, quantity=100
        )

        self.client = APIClient()
