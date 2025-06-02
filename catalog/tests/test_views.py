from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Category, Product
from decimal import Decimal

User = get_user_model()

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

    def test_product_list_pagination(self):
        """Тест пагинации на странице списка продуктов"""
        # Создаем достаточно продуктов для пагинации (9 на страницу)
        for i in range(15):
            Product.objects.create(
                name=f"Product {i}",
                description="Test Description",
                price=Decimal(f'{100 + i}.00'),
                category=self.category
            )

        # Тест первой страницы
        response = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(response.status_code, 200)
        # Проверяем, что на первой странице 9 продуктов + 1 созданный в setUp = 10 продуктов
        self.assertEqual(len(response.context['products']), 9)
        self.assertTrue(response.context['is_paginated'])
        self.assertIsNotNone(response.context['page_obj'].next_page_number)

        # Тест второй страницы
        response = self.client.get(reverse('catalog:product_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        # Проверяем, что на второй странице оставшиеся продукты (16 - 9 = 7)
        self.assertEqual(len(response.context['products']), 7)
        self.assertTrue(response.context['is_paginated'])
        self.assertIsNotNone(response.context['page_obj'].previous_page_number)

        # Тест несуществующей страницы
        response = self.client.get(reverse('catalog:product_list') + '?page=3')
        self.assertEqual(response.status_code, 404)

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

    def test_category_detail_pagination(self):
        """Тест пагинации на странице деталей категории"""
        # Создаем достаточно продуктов для пагинации в категории
        for i in range(15):
            Product.objects.create(
                name=f"Category Product {i}",
                description="Test Description",
                price=Decimal(f'{200 + i}.00'),
                category=self.category  # Связываем с тестовой категорией
            )

        # Тест первой страницы
        response = self.client.get(reverse('catalog:category_detail', kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        # Проверяем, что на первой странице 9 продуктов (1 созданный в setUp + 8 новых)
        # Важно: нужно учитывать продукт, созданный в setUp, если он тоже в этой категории
        # В данном случае он в тестовой категории, так что всего 16 продуктов (1 + 15)
        # На первой странице должно быть 9
        self.assertEqual(len(response.context['category'].products.all()), 16) # Проверяем общее количество
        self.assertEqual(len(response.context['products']), 9) # Проверяем количество на странице
        self.assertTrue(response.context['products'].has_other_pages)
        self.assertTrue(response.context['products'].has_next)

        # Тест второй страницы
        response = self.client.get(reverse('catalog:category_detail', kwargs={'slug': self.category.slug}) + '?page=2')
        self.assertEqual(response.status_code, 200)
        # Проверяем, что на второй странице оставшиеся продукты (16 - 9 = 7)
        self.assertEqual(len(response.context['products']), 7)
        self.assertTrue(response.context['products'].has_other_pages)
        self.assertTrue(response.context['products'].has_previous)

        # Тест несуществующей страницы
        response = self.client.get(reverse('catalog:category_detail', kwargs={'slug': self.category.slug}) + '?page=3')
        self.assertEqual(response.status_code, 404) 