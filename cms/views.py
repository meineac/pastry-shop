from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone as dj_tz

from .models import News, CompanyInfo, Vacancy, QaA, Review, NewsTag, VacancyTag, QaATag, ReviewTag, Partner, PromotionalBanner
from .forms import ReviewForm, CompanyInfoForm, NewsForm, VacancyForm, QaAForm, PromoCodeForm
from users.models import StaffProfile
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
    return render(request, 'cms/generic_form.html', {'form': form, 'title': title})

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
    return render(request, 'cms/generic_form.html', {'form': form, 'title': title})

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
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Edit About Company'})

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
    if not query and not tag_ids:
        news = news[:7]

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
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Edit Review'})

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
    employees = StaffProfile.objects.all()
    return render(request, 'cms/contacts.html', {'employees': employees})


# --- PRIVACY POLICY ---
def privacy_policy_view(request):
    return render(request, 'cms/privacy_policy.html')
