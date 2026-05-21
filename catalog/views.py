from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import Http404
from .models import Product, Category, Manufacturer
from cms.models import Review
from purchasing.models import Order, OrderItem
from users.decorators import role_required
from .forms import ProductForm

def product_list_view(request):
    if request.user.is_authenticated and request.user.role in ['ADMIN', 'STAFF']:
        products = Product.objects.all()
    else:
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
    product = get_object_or_404(Product, id=product_id)
    
    # Restrict inactive products to admins and staff only
    if not product.is_active:
        if not (request.user.is_authenticated and request.user.role in ['ADMIN', 'STAFF']):
            raise Http404("Product is not active.")

    reviews = Review.objects.filter(product=product)

    can_review = False
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        has_received = OrderItem.objects.filter(
            order__client=request.user.customer_profile,
            order__status=Order.OrderStatus.COMPLETED,
            product=product
        ).exists()
        already_reviewed = Review.objects.filter(
            author=request.user,
            product=product
        ).exists()
        can_review = has_received and not already_reviewed

    context = {
        'product': product,
        'reviews': reviews,
        'can_review': can_review,
    }
    return render(request, 'catalog/product_detail.html', context)

@role_required(['ADMIN', 'STAFF'])
def product_create_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return redirect('catalog:product_detail', product_id=product.id)
    else:
        form = ProductForm()
    return render(request, 'catalog/product_form.html', {'form': form, 'title': 'Create Product'})

@role_required(['ADMIN', 'STAFF'])
def product_edit_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('catalog:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'catalog/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})

@role_required(['ADMIN', 'STAFF'])
def product_delete_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('catalog:product_list')
    return render(request, 'catalog/product_confirm_delete.html', {'product': product})
