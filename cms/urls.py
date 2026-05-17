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

# Admin CRUD urls
urlpatterns += [
    re_path(r'^about/edit/$', views.about_company_edit_view, name='about_edit'),
    re_path(r'^news/add/$', views.news_create_view, name='news_create'),
    re_path(r'^news/(?P<pk>\d+)/edit/$', views.news_edit_view, name='news_edit'),
    re_path(r'^news/(?P<pk>\d+)/delete/$', views.news_delete_view, name='news_delete'),
    re_path(r'^vacancies/add/$', views.vacancy_create_view, name='vacancy_create'),
    re_path(r'^vacancies/(?P<pk>\d+)/edit/$', views.vacancy_edit_view, name='vacancy_edit'),
    re_path(r'^vacancies/(?P<pk>\d+)/delete/$', views.vacancy_delete_view, name='vacancy_delete'),
    re_path(r'^qna/add/$', views.qna_create_view, name='qna_create'),
    re_path(r'^qna/(?P<pk>\d+)/edit/$', views.qna_edit_view, name='qna_edit'),
    re_path(r'^qna/(?P<pk>\d+)/delete/$', views.qna_delete_view, name='qna_delete'),
    re_path(r'^promo-codes/add/$', views.promo_code_create_view, name='promo_code_create'),
    re_path(r'^promo-codes/(?P<pk>\d+)/edit/$', views.promo_code_edit_view, name='promo_code_edit'),
    re_path(r'^promo-codes/(?P<pk>\d+)/delete/$', views.promo_code_delete_view, name='promo_code_delete'),
]
