from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from product.models import Category, Product
from dj_rest_auth import views
from django.views.generic import CreateView



User = get_user_model()


class ProductTest(APITestCase):

    client = APIClient()

    def setUp(self):
        self.user = User.objects.create(username='masood')

        self.category = Category.objects.create(name='kir')

        self.product = Product.objects.create(
            name='test', price=100, seller_id=1, category_id=1, quantity=100)

    def test_list_product(self):

        url = reverse('product-list')

        resp = self.client.get(url, format='json')

        self.assertEqual(resp.status_code, 200)

    def test_folan(self):

        self.assertEqual(1, 1)
