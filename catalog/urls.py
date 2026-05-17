from django.urls import re_path
from . import views

app_name = 'catalog'

urlpatterns = [
    re_path(r'^catalog/$', views.product_list_view, name='product_list'),
    re_path(r'^catalog/(?P<product_id>\d+)/$', views.product_detail_view, name='product_detail'),
]
