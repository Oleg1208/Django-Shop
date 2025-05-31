from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class BaseCatalogItem(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='', blank=True, null=True, verbose_name='Изображение')

    class Meta:
        abstract = True


class Category(BaseCatalogItem):
    """Модель для категорий товаров"""
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Изображение')
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:category_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.full_clean()
        super().save(*args, **kwargs)


class Product(BaseCatalogItem):
    """Модель для товаров"""
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name='Категория')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    stock = models.PositiveIntegerField(default=0, verbose_name='Наличие')
    available = models.BooleanField(default=True, verbose_name='Доступен')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Изображение')
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.id, self.slug])

    def clean(self):
        if self.price < 0:
            raise ValidationError({'price': 'Цена не может быть отрицательной'})
        super().clean()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.full_clean()
        super().save(*args, **kwargs)


class Customer(models.Model):
    """Модель для покупателей"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адрес')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    """Модель для заказов"""
    ORDER_STATUS = (
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )
    
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.CASCADE, verbose_name='Покупатель')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='new', verbose_name='Статус')
    note = models.TextField(blank=True, verbose_name='Примечание')
    
    class Meta:
        ordering = ['-created']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
    def __str__(self):
        return f'Заказ {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    """Модель для элементов заказа"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name='Товар')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    
    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
    
    def __str__(self):
        return f'{self.id}'
    
    def get_cost(self):
        return self.price * self.quantity
