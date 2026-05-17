from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import News, CompanyInfo, Vacancy, QaA, Review, NewsTag, VacancyTag, QaATag, ReviewTag
from users.models import StaffProfile
from purchasing.models import PromoCode
from .forms import ReviewForm

def home_view(request):
    latest_news = News.objects.order_by('-created_at').first()
    return render(request, 'cms/home.html', {'latest_news': latest_news})

def about_company_view(request):
    company_info = CompanyInfo.objects.first()
    return render(request, 'cms/about.html', {'company_info': company_info})

def news_list_view(request):
    query = request.GET.get('q', '')
    tag_id = request.GET.get('tag', '')

    news = News.objects.all().order_by('-created_at')

    if tag_id:
        news = news.filter(tags__id=tag_id)

    if query:
        news = news.filter(
            Q(title__icontains=query) |
            Q(short_summary__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    tags = NewsTag.objects.all()

    return render(request, 'cms/news_list.html', {
        'news': news,
        'tags': tags,
        'current_tag': int(tag_id) if tag_id.isdigit() else '',
        'query': query
    })

def news_detail_view(request, pk):
    news_item = News.objects.get(pk=pk)
    return render(request, 'cms/news_detail.html', {'news_item': news_item})

def vacancies_list_view(request):
    query = request.GET.get('q', '')
    tag_id = request.GET.get('tag', '')

    vacancies = Vacancy.objects.all().order_by('-updated_at')

    if tag_id:
        vacancies = vacancies.filter(tags__id=tag_id)

    if query:
        vacancies = vacancies.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    tags = VacancyTag.objects.all()

    return render(request, 'cms/vacancies_list.html', {
        'vacancies': vacancies,
        'tags': tags,
        'current_tag': int(tag_id) if tag_id.isdigit() else '',
        'query': query
    })

def qna_list_view(request):
    query = request.GET.get('q', '')
    tag_id = request.GET.get('tag', '')

    qna = QaA.objects.all().order_by('-created_at')

    if tag_id:
        qna = qna.filter(tags__id=tag_id)

    if query:
        qna = qna.filter(
            Q(question_text__icontains=query) |
            Q(answer_text__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    tags = QaATag.objects.all()

    return render(request, 'cms/qna_list.html', {
        'qna': qna,
        'tags': tags,
        'current_tag': int(tag_id) if tag_id.isdigit() else '',
        'query': query
    })

def contacts_list_view(request):
    employees = StaffProfile.objects.all()
    return render(request, 'cms/contacts.html', {'employees': employees})

def privacy_policy_view(request):
    return render(request, 'cms/privacy_policy.html')

def reviews_list_view(request):
    reviews = Review.objects.filter(product__isnull=True).order_by('-created_at')
    return render(request, 'cms/reviews_list.html', {'reviews': reviews})

from django.core.exceptions import PermissionDenied

@login_required(login_url='/login/')
def review_create_view(request):
    if request.user.role != 'CUSTOMER':
        raise PermissionDenied("Only customers can create reviews.")

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.save()
            form.save_m2m() # Save tags
            return redirect('cms:reviews')
    else:
        form = ReviewForm()
    return render(request, 'cms/review_create.html', {'form': form})

def promo_codes_list_view(request):
    promo_codes = PromoCode.objects.all().order_by('-created_at')
    return render(request, 'cms/promo_codes.html', {'promo_codes': promo_codes})
