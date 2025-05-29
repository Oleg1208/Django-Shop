from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Category, Product
from decimal import Decimal

User = get_user_model()

class PermissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем обычного пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Создаем суперпользователя
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        # Создаем тестовые данные
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description"
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal('100.00'),
            category=self.category
        )

    def test_public_pages_access(self):
        """Тест доступа к публичным страницам"""
        urls = [
            reverse('catalog:category_list'),
            reverse('catalog:product_list'),
            reverse('catalog:category_detail', kwargs={'slug': self.category.slug}),
            reverse('catalog:product_detail', kwargs={'pk': self.product.id, 'slug': self.product.slug}),
            reverse('catalog:product_search'),
            reverse('users:login'),
            reverse('users:register'),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed to access {url}")

    def test_protected_pages_access(self):
        """Тест доступа к защищенным страницам"""
        # Тест без авторизации
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

        # Тест с авторизацией обычного пользователя
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)

    def test_admin_pages_access(self):
        """Тест доступа к админ-страницам"""
        admin_urls = [
            '/admin/',
            '/admin/catalog/category/',
            '/admin/catalog/product/',
            '/admin/users/user/',
        ]

        # Тест без авторизации
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Редирект на страницу входа админки

        # Тест с авторизацией обычного пользователя
        self.client.login(username='testuser', password='testpass123')
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Редирект на страницу входа админки

        # Тест с авторизацией суперпользователя
        self.client.login(username='admin', password='adminpass123')
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed to access {url}")

    def test_logout_redirect(self):
        """Тест редиректа после выхода из системы"""
        # Вход в систему
        self.client.login(username='testuser', password='testpass123')
        
        # Выход из системы
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # Редирект после выхода
        
        # Проверка, что после выхода нельзя получить доступ к защищенным страницам
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_invalid_login_attempts(self):
        """Тест попыток входа с неверными данными"""
        login_url = reverse('users:login')
        
        # Попытка входа с неверным паролем
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Попытка входа с несуществующим пользователем
        response = self.client.post(login_url, {
            'username': 'nonexistent',
            'password': 'anypass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated) 