"""
Statistics view for staff and admin users.

Provides:
  - Product list with review breakdown per rating and total sales count.
  - Statistical metrics (mean, mode, median) for completed order amounts.
  - Statistical metrics (mean, median) for client ages.
  - Most popular product category (by completed OrderItem count).
  - Most profitable product category (by total revenue from completed orders).
  - Matplotlib graphs (server-side, base64-encoded inline PNG):
      1. Purchases of a specific product by date.
      2. Purchases by product category (bar chart).
"""

import base64
import io
import logging
import statistics as stats_module
from datetime import date

import matplotlib
import matplotlib.pyplot as plt
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render

from catalog.models import Category, Product
from purchasing.models import Order, OrderItem
from users.decorators import role_required
from users.models import CustomerProfile, User

# Use non-interactive backend — mandatory for server-side rendering with no display.
matplotlib.use('Agg')

logger = logging.getLogger(__name__)


def _fig_to_base64(fig):
    """Render a matplotlib Figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return encoded


def _build_product_by_date_chart(product):
    """
    Line chart: number of completed purchases of `product` grouped by date.
    Returns a base64-encoded PNG string.
    """
    daily_data = (
        OrderItem.objects
        .filter(product=product, order__status=Order.OrderStatus.COMPLETED)
        .annotate(day=TruncDate('order__created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    if daily_data:
        dates = [row['day'] for row in daily_data]
        counts = [row['count'] for row in daily_data]
    else:
        dates, counts = [], []

    fig, ax = plt.subplots(figsize=(8, 4))
    if dates:
        ax.plot(dates, counts, marker='o', linewidth=2)
        ax.fill_between(dates, counts, alpha=0.15)
    else:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)

    ax.set_title(f'Purchases of "{product.name}" by Date')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of purchases')
    fig.autofmt_xdate()
    return _fig_to_base64(fig)


def _build_purchases_by_category_chart():
    """
    Bar chart: total completed purchases (OrderItem count) grouped by category.
    Returns a base64-encoded PNG string.
    """
    category_data = (
        OrderItem.objects
        .filter(order__status=Order.OrderStatus.COMPLETED, product__isnull=False)
        .values('product__category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    names = [row['product__category__name'] or 'Uncategorised' for row in category_data]
    counts = [row['count'] for row in category_data]

    fig, ax = plt.subplots(figsize=(8, 4))
    if names:
        bars = ax.bar(names, counts)
        ax.bar_label(bars)
    else:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)

    ax.set_title('Purchases by Product Category')
    ax.set_xlabel('Category')
    ax.set_ylabel('Number of purchases')
    fig.autofmt_xdate(rotation=30)
    return _fig_to_base64(fig)


def _sales_statistics():
    """
    Compute mean, mode, and median for completed Order final_price values.
    Returns a dict with keys: mean, mode (list), median, or None values when
    there is insufficient data.
    """
    prices = list(
        Order.objects
        .filter(status=Order.OrderStatus.COMPLETED)
        .values_list('final_price', flat=True)
    )
    # Convert Decimal to float for the statistics module
    prices_f = [float(p) for p in prices]

    if not prices_f:
        return {'mean': None, 'mode': None, 'median': None}

    mean_val = round(stats_module.mean(prices_f), 2)
    median_val = round(stats_module.median(prices_f), 2)

    try:
        mode_val = stats_module.mode(prices_f)
        mode_display = [round(mode_val, 2)]
    except stats_module.StatisticsError:
        # Python < 3.8 raises when there are multiple modes; fall back to multimode
        mode_display = [round(v, 2) for v in stats_module.multimode(prices_f)]

    return {'mean': mean_val, 'mode': mode_display, 'median': median_val}


def _age_statistics():
    """
    Compute mean and median age for all CustomerProfiles.
    Returns a dict with keys: mean, median, or None when there is no data.
    """
    today = date.today()
    ages = []
    for dob in CustomerProfile.objects.values_list('date_of_birth', flat=True):
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        ages.append(age)

    if not ages:
        return {'mean': None, 'median': None}

    return {
        'mean': round(stats_module.mean(ages), 2),
        'median': round(stats_module.median(ages), 2),
    }


def _category_popularity():
    """
    Returns categories ordered by number of completed OrderItems (most to least).
    Each entry has: name, item_count.
    """
    return (
        Category.objects
        .annotate(
            item_count=Count(
                'products__orderitem',
                filter=Q(
                    products__orderitem__order__status=Order.OrderStatus.COMPLETED
                )
            )
        )
        .order_by('-item_count')
        .values('name', 'item_count')
    )


def _category_profit():
    """
    Returns categories ordered by total revenue from completed orders
    (purchase_price * quantity), most to least.
    Each entry has: name, total_revenue.
    """
    return (
        Category.objects
        .annotate(
            total_revenue=Sum(
                ExpressionWrapper(
                    F('products__orderitem__purchase_price') * F('products__orderitem__quantity'),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                filter=Q(products__orderitem__order__status=Order.OrderStatus.COMPLETED)
            )
        )
        .order_by('-total_revenue')
        .values('name', 'total_revenue')
    )


def _product_stats_list():
    """
    For each product: photo, review counts per rating (0–5) + total, number
    of sales (completed OrderItem rows referencing this product).
    Returns a list of dicts.
    """
    products = Product.objects.prefetch_related('reviews').order_by('name')
    result = []
    for product in products:
        reviews = product.reviews.all()
        rating_counts = {r: 0 for r in range(6)}
        for review in reviews:
            rating_counts[review.rating] += 1
        sales_count = OrderItem.objects.filter(
            product=product,
            order__status=Order.OrderStatus.COMPLETED
        ).count()
        result.append({
            'product': product,
            'rating_counts': rating_counts,
            'total_reviews': sum(rating_counts.values()),
            'sales_count': sales_count,
        })
    return result


@role_required([User.Role.ADMIN, User.Role.STAFF])
def statistics_view(request):
    """
    Statistics page: product list with review/sales data, statistical metrics,
    and two server-side matplotlib graphs.
    """
    logger.info("Statistics page accessed by '%s'.", request.user.username)

    # --- Product list section ---
    product_stats = _product_stats_list()

    # --- Statistical metrics ---
    sales_stats = _sales_statistics()
    age_stats = _age_statistics()

    # --- Category rankings ---
    category_popularity = list(_category_popularity())
    category_profit = list(_category_profit())

    # --- Graph 1: purchases of a specific product by date ---
    all_products = Product.objects.order_by('name')
    selected_product_id = request.GET.get('product_id', '').strip()
    selected_product = None

    if selected_product_id and selected_product_id.isdigit():
        selected_product = Product.objects.filter(id=int(selected_product_id)).first()

    if selected_product is None and all_products.exists():
        selected_product = all_products.first()

    chart_product_b64 = None
    if selected_product:
        chart_product_b64 = _build_product_by_date_chart(selected_product)

    # --- Graph 2: purchases by category ---
    chart_category_b64 = _build_purchases_by_category_chart()

    context = {
        'product_stats': product_stats,
        'sales_stats': sales_stats,
        'age_stats': age_stats,
        'category_popularity': category_popularity,
        'category_profit': category_profit,
        'chart_product_b64': chart_product_b64,
        'chart_category_b64': chart_category_b64,
        'all_products': all_products,
        'selected_product': selected_product,
        'selected_product_id': selected_product_id,
        'rating_range': range(6),
    }
    return render(request, 'catalog/statistics.html', context)
