from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from catalog.models import Category, Product
from decimal import Decimal

User = get_user_model()

class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.login_url = reverse('users:login')
        self.register_url = reverse('users:register')
        self.profile_url = reverse('users:profile')
        self.logout_url = reverse('users:logout')

    def test_login_view_get(self):
        """Тест GET запроса страницы входа"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_view_post_success(self):
        """Тест успешного входа"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_view_post_invalid(self):
        """Тест входа с неверными данными"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'Пожалуйста, введите правильные имя пользователя и пароль')

    def test_register_view_get(self):
        """Тест GET запроса страницы регистрации"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_view_post_success(self):
        """Тест успешной регистрации"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешной регистрации
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_invalid(self):
        """Тест регистрации с неверными данными"""
        response = self.client.post(self.register_url, {
            'username': 'testuser',  # Уже существующий пользователь
            'email': 'test@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пользователь с таким именем уже существует')

    def test_profile_view_authenticated(self):
        """Тест просмотра профиля авторизованным пользователем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertContains(response, 'testuser')

    def test_profile_view_unauthenticated(self):
        """Тест просмотра профиля неавторизованным пользователем"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_logout_view(self):
        """Тест выхода из системы"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Редирект после выхода
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_profile_update(self):
        """Тест обновления профиля"""
        self.client.login(username='testuser', password='testpass123')
        update_url = reverse('users:profile_update')
        response = self.client.post(update_url, {
            'username': 'testuser',  # Добавляем username, так как он требуется
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после обновления
        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.email, 'updated@example.com')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'User')

    def test_logout_redirect(self):
        """Тест редиректа после выхода из системы"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # Редирект после выхода
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

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
