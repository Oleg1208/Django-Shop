from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Category, Product
from django.db.models import Q

# Create your views here.

class CategoryListView(ListView):
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.exclude(slug='').order_by('name')

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'catalog/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        product_list = category.products.all()

        paginator = Paginator(product_list, 9)  # 9 товаров на страницу
        page = self.request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            # Если страница не целое число, отображаем первую страницу.
            products = paginator.page(1)
        except EmptyPage:
            # Если страница вне диапазона (например, 9999), отображаем последнюю страницу.
            products = paginator.page(paginator.num_pages)

        context['products'] = products
        return context

class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

class ProductSearchView(ListView):
    model = Product
    template_name = 'catalog/product_search.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
