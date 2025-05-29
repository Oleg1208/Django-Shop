from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from catalog.models import Category, Product
from decimal import Decimal

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
        Category.objects.create(name="Test Category")
        with self.assertRaises(ValidationError):
            Category.objects.create(name="Test Category")

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
            Product.objects.create(
                name="Test Product",
                price=Decimal('150.00'),
                category=self.category
            )

    def test_product_get_absolute_url(self):
        """Тест метода get_absolute_url"""
        expected_url = f'/catalog/product/{self.product.id}/{self.product.slug}/'
        self.assertEqual(self.product.get_absolute_url(), expected_url) 