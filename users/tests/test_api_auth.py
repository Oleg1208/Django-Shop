from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from catalog.models import Category, Product, Customer, Order
from decimal import Decimal

User = get_user_model()

class APIAuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            address='Test Address'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('100.00'),
            category=self.category
        )
        self.order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('100.00')
        )

    def test_token_authentication(self):
        """Test token authentication endpoints"""
        # Test obtaining token
        url = reverse('users:api_token_auth')
        response = self.client.post(url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        token = response.data['token']

        # Test accessing protected endpoint with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get(reverse('api:customer-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test token refresh
        refresh_url = reverse('users:api_token_refresh')
        response = self.client.post(refresh_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertNotEqual(token, response.data['token'])

    def test_api_permissions(self):
        """Test API permissions for different user types"""
        # Get tokens for both users
        self.client.post(reverse('users:api_token_auth'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        user_token = self.client.post(reverse('users:api_token_auth'), {
            'username': 'testuser',
            'password': 'testpass123'
        }).data['token']

        self.client.post(reverse('users:api_token_auth'), {
            'username': 'admin',
            'password': 'adminpass123'
        })
        admin_token = self.client.post(reverse('users:api_token_auth'), {
            'username': 'admin',
            'password': 'adminpass123'
        }).data['token']

        # Test category permissions
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
        response = self.client.get(reverse('api:category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(reverse('api:category-list'), {
            'name': 'New Category',
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token}')
        response = self.client.post(reverse('api:category-list'), {
            'name': 'New Category',
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test order permissions
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {user_token}')
        response = self.client.get(reverse('api:order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only sees their own order

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token}')
        response = self.client.get(reverse('api:order-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Admin sees all orders

    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        # Test without token
        response = self.client.get(reverse('api:customer-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test with invalid token
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid-token')
        response = self.client.get(reverse('api:customer-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 