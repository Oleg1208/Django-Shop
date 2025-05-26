from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Product

class Command(BaseCommand):
    help = 'Проверяет и исправляет пустые slug\'и в категориях и товарах'

    def generate_unique_slug(self, model, name, current_slug=None):
        """Генерирует уникальный slug на основе имени"""
        base_slug = slugify(name)
        if not base_slug:  # Если имя не содержит букв/цифр
            base_slug = 'category'  # или 'product' для товаров
        
        slug = base_slug
        counter = 1
        while model.objects.filter(slug=slug).exclude(id=getattr(current_slug, 'id', None)).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def handle(self, *args, **options):
        # Проверяем и исправляем slug'и категорий
        categories = Category.objects.all()
        for category in categories:
            if not category.slug or category.slug.isspace():
                old_slug = category.slug
                category.slug = self.generate_unique_slug(Category, category.name, category)
                category.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Исправлен slug для категории "{category.name}": "{old_slug}" -> "{category.slug}"'
                    )
                )

        # Проверяем и исправляем slug'и товаров
        products = Product.objects.all()
        for product in products:
            if not product.slug or product.slug.isspace():
                old_slug = product.slug
                product.slug = self.generate_unique_slug(Product, product.name, product)
                product.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Исправлен slug для товара "{product.name}": "{old_slug}" -> "{product.slug}"'
                    )
                )

        self.stdout.write(self.style.SUCCESS('Проверка и исправление slug\'ов завершены')) 