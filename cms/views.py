import re
import time
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.urls import reverse
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone as dj_tz

from .models import News, CompanyInfo, Vacancy, QaA, Review, NewsTag, VacancyTag, QaATag, ReviewTag, Partner, PromotionalBanner
from .forms import ReviewForm, CompanyInfoForm, NewsForm, VacancyForm, QaAForm, PromoCodeForm
from users.models import User, StaffProfile
from purchasing.models import PromoCode, Order, OrderItem, Product
from catalog.models import Product as CatalogProduct
from users.decorators import role_required
from core.views import get_client_ip, get_ipinfo, get_weather, build_text_calendar, local_datetime

# --- GENERIC HELPERS ---
def generic_create_view(request, form_class, redirect_url, title):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = form_class()
    cancel_url = '/'
    if isinstance(redirect_url, str):
        try:
            cancel_url = reverse(redirect_url)
        except Exception:
            cancel_url = redirect_url
    return render(request, 'cms/generic_form.html', {'form': form, 'title': title, 'cancel_url': cancel_url})

def generic_edit_view(request, model, form_class, redirect_url, title, pk):
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            if callable(redirect_url):
                res = redirect_url(obj)
                if isinstance(res, tuple):
                    return redirect(res[0], *res[1:])
                return redirect(res)
            return redirect(redirect_url)
    else:
        form = form_class(instance=obj)
    cancel_url = '/'
    if callable(redirect_url):
        res = redirect_url(obj)
        if isinstance(res, tuple):
            try:
                cancel_url = reverse(res[0], args=res[1:])
            except Exception:
                cancel_url = '/'
        elif isinstance(res, str):
            try:
                cancel_url = reverse(res)
            except Exception:
                cancel_url = res
    elif isinstance(redirect_url, str):
        try:
            cancel_url = reverse(redirect_url)
        except Exception:
            cancel_url = redirect_url
    return render(request, 'cms/generic_form.html', {'form': form, 'title': title, 'cancel_url': cancel_url})

def generic_delete_view(request, model, redirect_url, title, pk):
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect(redirect_url)
    return render(request, 'cms/generic_confirm_delete.html', {'object': obj, 'title': title, 'cancel_url': redirect_url})


# --- HOME ---
def home_view(request):
    latest_news = News.objects.filter(is_hidden=False).order_by('-created_at').first()
    products_preview = CatalogProduct.objects.filter(is_active=True).order_by('id')[:4]
    partners = Partner.objects.filter(is_hidden=False)
    banners = PromotionalBanner.objects.filter(is_active=True)
    company_info = CompanyInfo.objects.filter(is_hidden=False).first()

    # --- User location / timezone / weather / calendar ---
    ip = get_client_ip(request)
    location = get_ipinfo(ip)

    tz_name = location.get("timezone", "UTC") or "UTC"
    city = location.get("city", "Unknown")
    country = location.get("country", "Unknown")

    local_dt = local_datetime(tz_name)
    weather = get_weather(city, country)
    text_calendar = build_text_calendar(local_dt.year, local_dt.month)

    utc_now = dj_tz.now()

    context = {
        'latest_news': latest_news,
        'products_preview': products_preview,
        'partners': partners,
        'banners': banners,
        'company_info': company_info,
        # location block
        'ip': ip,
        'city': city,
        'country': country,
        'timezone': tz_name,
        'local_date': local_dt.strftime("%d/%m/%Y"),
        'local_time': local_dt.strftime("%H:%M:%S"),
        'utc_date': utc_now.strftime("%d/%m/%Y"),
        'weather': weather,
        'text_calendar': text_calendar,
        # full datetime objects for timezone display
        'now_utc': utc_now,
        'now_local': local_dt,
        'tz_name': tz_name,
    }
    return render(request, 'cms/home.html', context)


# --- COMPANY INFO ---
def about_company_view(request):
    company_info = CompanyInfo.objects.filter(is_hidden=False).first()
    return render(request, 'cms/about.html', {'company_info': company_info})

@role_required(['ADMIN'])
def about_company_edit_view(request):
    company_info = CompanyInfo.objects.first()
    if request.method == 'POST':
        form = CompanyInfoForm(request.POST, request.FILES, instance=company_info)
        if form.is_valid():
            form.save()
            return redirect('cms:about')
    else:
        form = CompanyInfoForm(instance=company_info)
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Edit About Company', 'cancel_url': reverse('cms:about')})

# --- NEWS ---
def news_list_view(request):
    query = request.GET.get('q', '')
    tag_ids = request.GET.getlist('tags')

    news = News.objects.filter(is_hidden=False).order_by('-created_at')

    if tag_ids:
        for tag_id in tag_ids:
            if tag_id.isdigit():
                news = news.filter(tags__id=tag_id)

    if query:
        news = news.filter(
            Q(title__icontains=query) |
            Q(short_summary__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    tags = NewsTag.objects.filter(news_articles__isnull=False).distinct()

    return render(request, 'cms/news_list.html', {
        'news': news,
        'tags': tags,
        'current_tags': [int(t) for t in tag_ids if t.isdigit()],
        'query': query
    })

def news_detail_view(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    return render(request, 'cms/news_detail.html', {'news_item': news_item})

@role_required(['ADMIN'])
def news_create_view(request):
    return generic_create_view(request, NewsForm, 'cms:news_list', 'Add News')

@role_required(['ADMIN'])
def news_edit_view(request, pk):
    return generic_edit_view(request, News, NewsForm, lambda obj: ('cms:news_detail', getattr(obj, 'pk', obj.id)), 'Edit News', pk)

@role_required(['ADMIN'])
def news_delete_view(request, pk):
    return generic_delete_view(request, News, 'cms:news_list', 'Delete News', pk)

# --- VACANCIES ---
def vacancies_list_view(request):
    query = request.GET.get('q', '')
    tag_ids = request.GET.getlist('tags')

    vacancies = Vacancy.objects.filter(is_hidden=False).order_by('-updated_at')

    if tag_ids:
        for tag_id in tag_ids:
            if tag_id.isdigit():
                vacancies = vacancies.filter(tags__id=tag_id)

    if query:
        vacancies = vacancies.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    tags = VacancyTag.objects.filter(vacancies__isnull=False).distinct()

    return render(request, 'cms/vacancies_list.html', {
        'vacancies': vacancies,
        'tags': tags,
        'current_tags': [int(t) for t in tag_ids if t.isdigit()],
        'query': query
    })

@role_required(['ADMIN'])
def vacancy_create_view(request):
    return generic_create_view(request, VacancyForm, 'cms:vacancies_list', 'Add Vacancy')

@role_required(['ADMIN'])
def vacancy_edit_view(request, pk):
    return generic_edit_view(request, Vacancy, VacancyForm, 'cms:vacancies_list', 'Edit Vacancy', pk)

@role_required(['ADMIN'])
def vacancy_delete_view(request, pk):
    return generic_delete_view(request, Vacancy, 'cms:vacancies_list', 'Delete Vacancy', pk)

# --- Q&A ---
def qna_list_view(request):
    query = request.GET.get('q', '')
    tag_ids = request.GET.getlist('tags')

    qna = QaA.objects.filter(is_hidden=False).order_by('-created_at')

    if tag_ids:
        for tag_id in tag_ids:
            if tag_id.isdigit():
                qna = qna.filter(tags__id=tag_id)

    if query:
        qna = qna.filter(
            Q(question_text__icontains=query) |
            Q(answer_text__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    tags = QaATag.objects.filter(qnas__isnull=False).distinct()

    return render(request, 'cms/qna_list.html', {
        'qna': qna,
        'tags': tags,
        'current_tags': [int(t) for t in tag_ids if t.isdigit()],
        'query': query
    })

@role_required(['ADMIN'])
def qna_create_view(request):
    return generic_create_view(request, QaAForm, 'cms:qna_list', 'Add Q&A')

@role_required(['ADMIN'])
def qna_edit_view(request, pk):
    return generic_edit_view(request, QaA, QaAForm, 'cms:qna_list', 'Edit Q&A', pk)

@role_required(['ADMIN'])
def qna_delete_view(request, pk):
    return generic_delete_view(request, QaA, 'cms:qna_list', 'Delete Q&A', pk)

# --- REVIEWS ---
def reviews_list_view(request):
    reviews = Review.objects.filter(product__isnull=True).order_by('-created_at')
    return render(request, 'cms/reviews_list.html', {'reviews': reviews})

@role_required(['CUSTOMER'])
def review_create_view(request):
    product_id = request.GET.get('product_id') or request.POST.get('product_id')
    product = None
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        
        if not hasattr(request.user, 'customer_profile'):
            messages.error(request, "Only customer accounts can leave product reviews.")
            return redirect('catalog:product_detail', product_id=product.id)
            
        has_received = OrderItem.objects.filter(
            order__client=request.user.customer_profile,
            order__status=Order.OrderStatus.COMPLETED,
            product=product
        ).exists()
        
        if not has_received:
            messages.error(request, "You can only leave a review for a product after you have received it.")
            return redirect('catalog:product_detail', product_id=product.id)
            
        already_reviewed = Review.objects.filter(
            author=request.user,
            product=product
        ).exists()
        
        if already_reviewed:
            messages.error(request, "You have already reviewed this product. You can only review a product once.")
            return redirect('catalog:product_detail', product_id=product.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            if product:
                review.product = product
            review.save()
            form.save_m2m() # Save tags
            if product:
                return redirect('catalog:product_detail', product_id=product.id)
            return redirect('cms:reviews')
    else:
        form = ReviewForm()
        
    title = f"Leave a Review for {product.name}" if product else "Add a Store Review"
    return render(request, 'cms/review_create.html', {'form': form, 'title': title, 'product': product})

@role_required(['CUSTOMER'])
def review_edit_view(request, pk):
    review = get_object_or_404(Review, pk=pk, author=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('cms:reviews')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Edit Review', 'cancel_url': reverse('cms:reviews')})

@role_required(['CUSTOMER'])
def review_delete_view(request, pk):
    review = get_object_or_404(Review, pk=pk, author=request.user)
    if request.method == 'POST':
        review.delete()
        return redirect('cms:reviews')
    return render(request, 'cms/generic_confirm_delete.html', {'object': review, 'title': 'Delete Review', 'cancel_url': 'cms:reviews'})


# --- PROMO CODES ---
def promo_codes_list_view(request):
    active_promos = PromoCode.objects.filter(
        is_hidden=False, status=PromoCode.Status.ACTIVE
    ).order_by('-created_at')
    archived_promos = PromoCode.objects.filter(
        is_hidden=False, status=PromoCode.Status.ARCHIVED
    ).order_by('-created_at')
    return render(request, 'cms/promo_codes.html', {
        'active_promos': active_promos,
        'archived_promos': archived_promos,
    })

@role_required(['ADMIN'])
def promo_code_create_view(request):
    return generic_create_view(request, PromoCodeForm, 'cms:promo_codes', 'Add Promo Code')

@role_required(['ADMIN'])
def promo_code_edit_view(request, pk):
    return generic_edit_view(request, PromoCode, PromoCodeForm, 'cms:promo_codes', 'Edit Promo Code', pk)

@role_required(['ADMIN'])
def promo_code_delete_view(request, pk):
    return generic_delete_view(request, PromoCode, 'cms:promo_codes', 'Delete Promo Code', pk)


# --- CONTACTS ---
def contacts_list_view(request):
    """
    Renders the contacts page. For regular visitors, it shows store info, map,
    and the employee cards. For authenticated admin users, it also enables
    the interactive contacts directory table.
    """
    employees = StaffProfile.objects.select_related('user').all().order_by('id')
    return render(request, 'cms/contacts.html', {'employees': employees})


def contacts_api_view(request):
    """
    JSON API endpoint returning all staff records from the database.
    Used by the client-side interactive table to load records asynchronously.
    """
    employees = StaffProfile.objects.select_related('user').all().order_by('id')
    staff_data = []
    for emp in employees:
        photo_url = emp.photo.url if emp.photo else ''
        staff_data.append({
            'id': emp.id,
            'full_name': emp.user.get_full_name() or emp.user.username,
            'first_name': emp.user.first_name,
            'last_name': emp.user.last_name or emp.user.username,
            'email': emp.user.email,
            'position': emp.position,
            'phone': emp.contact_details,
            'date_of_birth': emp.date_of_birth.strftime('%Y-%m-%d') if emp.date_of_birth else '',
            'url': emp.url,
            'photo_url': photo_url,
        })
    return JsonResponse({'status': 'ok', 'staff': staff_data})


@role_required(['ADMIN'])
@require_POST
def contacts_api_add_view(request):
    """
    Admin-only JSON API endpoint for creating a new employee in the database.
    Accepts multipart/form-data for photo file upload and all required model fields.
    Validates URL and phone number according to LR3 criteria.
    """
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    position = request.POST.get('position', '').strip()
    phone = request.POST.get('phone', '').strip()
    dob_str = request.POST.get('date_of_birth', '').strip()
    url = request.POST.get('url', '').strip()
    photo_file = request.FILES.get('photo')

    # Ensure all required text fields are provided
    if not (first_name and last_name and email and position and phone and dob_str and url):
        return JsonResponse({
            'status': 'error',
            'message': 'All required fields (first name, last name, email, position, phone, date of birth, URL) must be filled.'
        }, status=400)

    # Criteria validation: URL must start with http:// or https:// and end with .php or .html
    url_pattern = re.compile(r'^https?://.+\.(php|html)$', re.IGNORECASE)
    if not url_pattern.match(url):
        return JsonResponse({
            'status': 'error',
            'message': 'URL must start with http:// or https:// and end with .php or .html (e.g. http://site.ru/index.php).'
        }, status=400)

    # Criteria validation: Phone must start with +375 or 8, operator code with or without parens, rest with hyphens/spaces
    phone_pattern = re.compile(r'^(?:\+375|8)\s*\(?\d{2}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$')
    if not phone_pattern.match(phone):
        return JsonResponse({
            'status': 'error',
            'message': 'Phone must start with +375 or 8, followed by a valid 2-digit operator code and 7 digits (e.g. +375 (29) 111-22-33 or 80291112233).'
        }, status=400)

    # Validate date of birth
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid date of birth format. Expected YYYY-MM-DD.'
        }, status=400)

    # Generate a unique username for the staff user
    base_username = re.sub(r'[^a-zA-Z0-9]', '', f"{first_name.lower()}_{last_name.lower()}")
    if not base_username:
        base_username = f"staff_{int(time.time())}"
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    with transaction.atomic():
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=User.Role.STAFF,
        )
        user.set_password('staffpass123')
        user.save()

        profile = StaffProfile(
            user=user,
            position=position,
            contact_details=phone,
            date_of_birth=dob,
            url=url,
        )
        if photo_file:
            profile.photo = photo_file
        profile.save()

    photo_url = profile.photo.url if profile.photo else ''
    return JsonResponse({
        'status': 'ok',
        'message': 'Employee created successfully.',
        'employee': {
            'id': profile.id,
            'full_name': user.get_full_name() or user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'position': profile.position,
            'phone': profile.contact_details,
            'date_of_birth': profile.date_of_birth.strftime('%Y-%m-%d'),
            'url': profile.url,
            'photo_url': photo_url,
        }
    })


# --- PRIVACY POLICY ---
def privacy_policy_view(request):
    return render(request, 'cms/privacy_policy.html')
