from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Product, Category, Manufacturer
from cms.models import Review

def product_list_view(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    manufacturer_id = request.GET.get('manufacturer', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query)
        )
    if category_id:
        products = products.filter(category_id=category_id)
    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id)
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    context = {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers,
        'query': query,
        'category_id': category_id,
        'manufacturer_id': manufacturer_id,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'catalog/product_list.html', context)

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = Review.objects.filter(product=product)

    context = {
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'catalog/product_detail.html', context)
