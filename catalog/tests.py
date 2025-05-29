from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from .models import Category, Product
from decimal import Decimal
from django.db.utils import IntegrityError

User = get_user_model()

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description"
        )

    def test_category_creation(self):
        """Тест создания категории"""
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.description, "Test Description")
        self.assertEqual(self.category.slug, slugify("Test Category"))
        self.assertTrue(isinstance(self.category, Category))
        self.assertEqual(str(self.category), self.category.name)

    def test_category_slug_auto_generation(self):
        """Тест автоматической генерации slug"""
        category = Category.objects.create(name="Another Category")
        self.assertEqual(category.slug, "another-category")

    def test_category_unique_slug(self):
        """Тест уникальности slug"""
        category = Category.objects.create(name="Test Category")
        with self.assertRaises(ValidationError):
            category2 = Category(name="Test Category")
            category2.full_clean()

class ProductModelTest(TestCase):
    def setUp(self):
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

    def test_product_creation(self):
        """Тест создания продукта"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.description, "Test Description")
        self.assertEqual(self.product.price, Decimal('100.00'))
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.slug, slugify("Test Product"))
        self.assertTrue(isinstance(self.product, Product))
        self.assertEqual(str(self.product), self.product.name)

    def test_product_price_validation(self):
        """Тест валидации цены продукта"""
        with self.assertRaises(ValidationError):
            Product.objects.create(
                name="Invalid Price Product",
                price=Decimal('-100.00'),
                category=self.category
            )

    def test_product_slug_auto_generation(self):
        """Тест автоматической генерации slug для продукта"""
        product = Product.objects.create(
            name="Another Product",
            price=Decimal('200.00'),
            category=self.category
        )
        self.assertEqual(product.slug, "another-product")

    def test_product_unique_slug(self):
        """Тест уникальности slug продукта"""
        with self.assertRaises(ValidationError):
            product2 = Product(
                name="Test Product",
                price=Decimal('150.00'),
                category=self.category
            )
            product2.full_clean()

    def test_product_get_absolute_url(self):
        """Тест метода get_absolute_url"""
        expected_url = f'/catalog/product/{self.product.id}/{self.product.slug}/'
        self.assertEqual(self.product.get_absolute_url(), expected_url)

class CatalogViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
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

    def test_category_list_view(self):
        """Тест представления списка категорий"""
        response = self.client.get(reverse('catalog:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/category_list.html')
        self.assertContains(response, self.category.name)

    def test_category_detail_view(self):
        """Тест представления детальной информации о категории"""
        response = self.client.get(reverse('catalog:category_detail', 
                                         kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/category_detail.html')
        self.assertContains(response, self.category.name)
        self.assertContains(response, self.product.name)

    def test_product_list_view(self):
        """Тест представления списка продуктов"""
        response = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/product_list.html')
        self.assertContains(response, self.product.name)

    def test_product_detail_view(self):
        """Тест представления детальной информации о продукте"""
        response = self.client.get(reverse('catalog:product_detail', 
                                         kwargs={'pk': self.product.id, 
                                                'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/product_detail.html')
        self.assertContains(response, self.product.name)
        self.assertContains(response, str(self.product.price))

    def test_product_search_view(self):
        """Тест представления поиска продуктов"""
        # Тест поиска по названию
        response = self.client.get(reverse('catalog:product_search'), 
                                 {'q': 'Test Product'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/product_search.html')
        self.assertContains(response, self.product.name)

        # Тест поиска по описанию
        response = self.client.get(reverse('catalog:product_search'), 
                                 {'q': 'Test Description'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

        # Тест пустого поиска
        response = self.client.get(reverse('catalog:product_search'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Результаты поиска')

    def test_invalid_category_detail(self):
        """Тест несуществующей категории"""
        response = self.client.get(reverse('catalog:category_detail', 
                                         kwargs={'slug': 'non-existent'}))
        self.assertEqual(response.status_code, 404)

    def test_invalid_product_detail(self):
        """Тест несуществующего продукта"""
        response = self.client.get(reverse('catalog:product_detail', 
                                         kwargs={'pk': 999, 
                                                'slug': 'non-existent'}))
        self.assertEqual(response.status_code, 404)
