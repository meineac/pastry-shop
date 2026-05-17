from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models import Tag
from .models import News, CompanyInfo, Vacancy, QaA, Review
from users.models import StaffProfile
from purchasing.models import PromoCode
from .forms import ReviewForm

def home_view(request):
    latest_news = News.objects.filter(is_hidden=False).order_by('-created_at').first()
    return render(request, 'cms/home.html', {'latest_news': latest_news})

def about_company_view(request):
    company_info = CompanyInfo.objects.filter(is_hidden=False).first()
    return render(request, 'cms/about.html', {'company_info': company_info})

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

    tags = Tag.objects.filter(news_articles__isnull=False).distinct()

    return render(request, 'cms/news_list.html', {
        'news': news,
        'tags': tags,
        'current_tags': [int(t) for t in tag_ids if t.isdigit()],
        'query': query
    })

def news_detail_view(request, pk):
    news_item = News.objects.get(pk=pk)
    return render(request, 'cms/news_detail.html', {'news_item': news_item})

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

    tags = Tag.objects.filter(vacancies__isnull=False).distinct()

    return render(request, 'cms/vacancies_list.html', {
        'vacancies': vacancies,
        'tags': tags,
        'current_tags': [int(t) for t in tag_ids if t.isdigit()],
        'query': query
    })

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

    tags = Tag.objects.filter(qnas__isnull=False).distinct()

    return render(request, 'cms/qna_list.html', {
        'qna': qna,
        'tags': tags,
        'current_tags': [int(t) for t in tag_ids if t.isdigit()],
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

from users.decorators import role_required

@login_required(login_url='/login/')
@role_required(['CUSTOMER'])
def review_create_view(request):
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
    promo_codes = PromoCode.objects.filter(is_hidden=False).order_by('-created_at')
    return render(request, 'cms/promo_codes.html', {'promo_codes': promo_codes})

from .forms import CompanyInfoForm, NewsForm, VacancyForm, QaAForm, PromoCodeForm
from django.shortcuts import get_object_or_404

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def about_company_edit_view(request):
    company_info = CompanyInfo.objects.first()
    if request.method == 'POST':
        form = CompanyInfoForm(request.POST, instance=company_info)
        if form.is_valid():
            form.save()
            return redirect('cms:about')
    else:
        form = CompanyInfoForm(instance=company_info)
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Edit About Company'})

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def news_create_view(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('cms:news_list')
    else:
        form = NewsForm()
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Add News'})

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def news_edit_view(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news_item)
        if form.is_valid():
            form.save()
            return redirect('cms:news_detail', pk=pk)
    else:
        form = NewsForm(instance=news_item)
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Edit News'})

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def news_delete_view(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        news_item.delete()
        return redirect('cms:news_list')
    return render(request, 'cms/generic_confirm_delete.html', {'object': news_item, 'title': 'Delete News', 'cancel_url': 'cms:news_list'})


@login_required(login_url='/login/')
@role_required(['ADMIN'])
def vacancy_create_view(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cms:vacancies_list')
    else:
        form = VacancyForm()
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Add Vacancy'})

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def vacancy_edit_view(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=vacancy)
        if form.is_valid():
            form.save()
            return redirect('cms:vacancies_list')
    else:
        form = VacancyForm(instance=vacancy)
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Edit Vacancy'})

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def vacancy_delete_view(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    if request.method == 'POST':
        vacancy.delete()
        return redirect('cms:vacancies_list')
    return render(request, 'cms/generic_confirm_delete.html', {'object': vacancy, 'title': 'Delete Vacancy', 'cancel_url': 'cms:vacancies_list'})


@login_required(login_url='/login/')
@role_required(['ADMIN'])
def qna_create_view(request):
    if request.method == 'POST':
        form = QaAForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cms:qna_list')
    else:
        form = QaAForm()
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Add Q&A'})

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def qna_edit_view(request, pk):
    qna = get_object_or_404(QaA, pk=pk)
    if request.method == 'POST':
        form = QaAForm(request.POST, instance=qna)
        if form.is_valid():
            form.save()
            return redirect('cms:qna_list')
    else:
        form = QaAForm(instance=qna)
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Edit Q&A'})

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def qna_delete_view(request, pk):
    qna = get_object_or_404(QaA, pk=pk)
    if request.method == 'POST':
        qna.delete()
        return redirect('cms:qna_list')
    return render(request, 'cms/generic_confirm_delete.html', {'object': qna, 'title': 'Delete Q&A', 'cancel_url': 'cms:qna_list'})

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def promo_code_create_view(request):
    if request.method == 'POST':
        form = PromoCodeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cms:promo_codes')
    else:
        form = PromoCodeForm()
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Add Promo Code'})

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def promo_code_edit_view(request, pk):
    promo = get_object_or_404(PromoCode, pk=pk)
    if request.method == 'POST':
        form = PromoCodeForm(request.POST, instance=promo)
        if form.is_valid():
            form.save()
            return redirect('cms:promo_codes')
    else:
        form = PromoCodeForm(instance=promo)
    return render(request, 'cms/generic_form.html', {'form': form, 'title': 'Edit Promo Code'})

@login_required(login_url='/login/')
@role_required(['ADMIN'])
def promo_code_delete_view(request, pk):
    promo = get_object_or_404(PromoCode, pk=pk)
    if request.method == 'POST':
        promo.delete()
        return redirect('cms:promo_codes')
    return render(request, 'cms/generic_confirm_delete.html', {'object': promo, 'title': 'Delete Promo Code', 'cancel_url': 'cms:promo_codes'})
