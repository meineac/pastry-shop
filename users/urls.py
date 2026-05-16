from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^login/$', views.login_view, name='login'),
    re_path(r'^logout/$', views.logout_view, name='logout'),
    re_path(r'^register/$', views.register_view, name='register'),

    re_path(r'^profile/$', views.profile_view, name='profile'),
    re_path(r'^profile/orders/$', views.order_history_view, name='order_history'),
    re_path(r'^profile/orders/(?P<order_id>\d+)/$', views.order_details_view, name='order_details'),

    re_path(r'^staff/$', views.staff_list_view, name='staff_list'),
]
