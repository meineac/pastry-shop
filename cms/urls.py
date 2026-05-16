from django.urls import re_path
from . import views

app_name = 'cms'

urlpatterns = [
    re_path(r'^$', views.home_view, name='home'),
    re_path(r'^about/$', views.about_company_view, name='about'),
    re_path(r'^news/$', views.news_list_view, name='news_list'),
    re_path(r'^news/(?P<pk>\d+)/$', views.news_detail_view, name='news_detail'),
    re_path(r'^vacancies/$', views.vacancies_list_view, name='vacancies_list'),
    re_path(r'^qna/$', views.qna_list_view, name='qna_list'),
    re_path(r'^contacts/$', views.contacts_list_view, name='contacts_list'),
    re_path(r'^privacy-policy/$', views.privacy_policy_view, name='privacy_policy'),
    re_path(r'^reviews/$', views.reviews_list_view, name='reviews'),
    re_path(r'^reviews/add/$', views.review_create_view, name='review_create'),
    re_path(r'^promo-codes/$', views.promo_codes_list_view, name='promo_codes'),
]
