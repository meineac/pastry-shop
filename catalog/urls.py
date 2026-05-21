from django.urls import re_path

from . import views
from . import views_stats

app_name = 'catalog'

urlpatterns = [
    re_path(r'^catalog/$', views.product_list_view, name='product_list'),
    re_path(r'^catalog/create/$', views.product_create_view, name='product_create'),
    re_path(r'^catalog/(?P<product_id>\d+)/$', views.product_detail_view, name='product_detail'),
    re_path(r'^catalog/(?P<product_id>\d+)/edit/$', views.product_edit_view, name='product_edit'),
    re_path(r'^catalog/(?P<product_id>\d+)/delete/$', views.product_delete_view, name='product_delete'),
    re_path(r'^statistics/$', views_stats.statistics_view, name='statistics'),
]
