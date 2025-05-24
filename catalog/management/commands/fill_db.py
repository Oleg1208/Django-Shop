import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import Category, Product, Customer, Order, OrderItem
from django.utils.text import slugify
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными для интернет-магазина'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем заполнение базы данных...')
        
        # Создаем категории
        categories_data = [
            {
                'name': 'Электроника',
                'description': 'Электронные устройства и гаджеты'
            },
            {
                'name': 'Одежда',
                'description': 'Мужская и женская одежда'
            },
            {
                'name': 'Книги',
                'description': 'Художественная и научная литература'
            },
            {
                'name': 'Спорт',
                'description': 'Спортивные товары и инвентарь'
            },
            {
                'name': 'Дом и сад',
                'description': 'Товары для дома и сада'
            }
        ]
        
        # Очищаем существующие данные
        self.stdout.write('Удаление существующих данных...')
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Customer.objects.all().delete()
        
        # Создаем категории
        self.stdout.write('Создание категорий...')
        categories = []
        for cat_data in categories_data:
            # Проверяем, существует ли уже категория с таким slug
            slug = slugify(cat_data['name'])
            if Category.objects.filter(slug=slug).exists():
                self.stdout.write(f'Категория с slug {slug} уже существует, пропускаем')
                continue
                
            category = Category.objects.create(
                name=cat_data['name'],
                slug=slug,
                description=cat_data['description']
            )
            categories.append(category)
            self.stdout.write(f'Создана категория: {category.name}')
        
        # Создаем продукты
        self.stdout.write('Создание продуктов...')
        products_data = [
            # Электроника
            {
                'category': 'Электроника',
                'name': 'Смартфон XYZ',
                'description': 'Мощный смартфон с отличной камерой',
                'price': '29999.99',
                'stock': 15
            },
            {
                'category': 'Электроника',
                'name': 'Ноутбук ABC',
                'description': 'Легкий и производительный ноутбук',
                'price': '54999.99',
                'stock': 8
            },
            {
                'category': 'Электроника',
                'name': 'Наушники Pro',
                'description': 'Беспроводные наушники с шумоподавлением',
                'price': '8999.99',
                'stock': 25
            },
            # Одежда
            {
                'category': 'Одежда',
                'name': 'Джинсы классические',
                'description': 'Классические джинсы синего цвета',
                'price': '2999.99',
                'stock': 30
            },
            {
                'category': 'Одежда',
                'name': 'Футболка хлопковая',
                'description': 'Хлопковая футболка белого цвета',
                'price': '999.99',
                'stock': 50
            },
            # Книги
            {
                'category': 'Книги',
                'name': 'Мастер и Маргарита',
                'description': 'Роман Михаила Булгакова',
                'price': '599.99',
                'stock': 20
            },
            {
                'category': 'Книги',
                'name': 'Python для начинающих',
                'description': 'Учебник по программированию на Python',
                'price': '1299.99',
                'stock': 15
            },
            # Спорт
            {
                'category': 'Спорт',
                'name': 'Гантели 5кг',
                'description': 'Пара гантелей по 5 кг',
                'price': '1999.99',
                'stock': 12
            },
            {
                'category': 'Спорт',
                'name': 'Скакалка спортивная',
                'description': 'Скакалка для тренировок',
                'price': '499.99',
                'stock': 35
            },
            # Дом и сад
            {
                'category': 'Дом и сад',
                'name': 'Набор посуды',
                'description': 'Набор кухонной посуды из 10 предметов',
                'price': '4999.99',
                'stock': 10
            },
            {
                'category': 'Дом и сад',
                'name': 'Комнатное растение',
                'description': 'Декоративное растение для дома',
                'price': '899.99',
                'stock': 18
            }
        ]
        
        products = []
        for prod_data in products_data:
            try:
                category = Category.objects.get(name=prod_data['category'])
                
                # Проверяем, существует ли уже продукт с таким slug
                slug = slugify(prod_data['name'])
                if Product.objects.filter(slug=slug).exists():
                    self.stdout.write(f'Продукт с slug {slug} уже существует, пропускаем')
                    continue
                    
                product = Product.objects.create(
                    category=category,
                    name=prod_data['name'],
                    slug=slug,
                    description=prod_data['description'],
                    price=Decimal(prod_data['price']),
                    stock=prod_data['stock']
                )
                products.append(product)
                self.stdout.write(f'Создан продукт: {product.name}')
            except Category.DoesNotExist:
                self.stdout.write(f'Категория {prod_data["category"]} не найдена, пропускаем продукт {prod_data["name"]}')
        
        # Создаем покупателей
        self.stdout.write('Создание покупателей...')
        customers_data = [
            {
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'email': 'ivan@example.com',
                'phone': '+7 (900) 123-45-67',
                'address': 'г. Москва, ул. Примерная, д. 1, кв. 10'
            },
            {
                'first_name': 'Мария',
                'last_name': 'Петрова',
                'email': 'maria@example.com',
                'phone': '+7 (900) 987-65-43',
                'address': 'г. Санкт-Петербург, пр. Невский, д. 20, кв. 5'
            },
            {
                'first_name': 'Алексей',
                'last_name': 'Сидоров',
                'email': 'alex@example.com',
                'phone': '+7 (900) 555-55-55',
                'address': 'г. Казань, ул. Центральная, д. 15, кв. 7'
            }
        ]
        
        customers = []
        for cust_data in customers_data:
            # Проверяем, существует ли уже покупатель с таким email
            if Customer.objects.filter(email=cust_data['email']).exists():
                self.stdout.write(f'Покупатель с email {cust_data["email"]} уже существует, пропускаем')
                continue
                
            customer = Customer.objects.create(
                first_name=cust_data['first_name'],
                last_name=cust_data['last_name'],
                email=cust_data['email'],
                phone=cust_data['phone'],
                address=cust_data['address']
            )
            customers.append(customer)
            self.stdout.write(f'Создан покупатель: {customer.first_name} {customer.last_name}')
        
        # Создаем заказы только если есть покупатели и продукты
        if customers and products:
            self.stdout.write('Создание заказов...')
            for i, customer in enumerate(customers):
                order = Order.objects.create(
                    customer=customer,
                    status=random.choice(['new', 'processing', 'shipped']),
                    note=f'Тестовый заказ #{i+1}'
                )
                
                # Добавляем товары в заказ
                num_items = min(random.randint(1, 3), len(products))
                selected_products = random.sample(products, num_items)
                
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=product.price,
                        quantity=quantity
                    )
                
                self.stdout.write(f'Создан заказ #{order.id} для {customer.first_name} {customer.last_name}')
        else:
            self.stdout.write('Недостаточно данных для создания заказов')
        
        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))
