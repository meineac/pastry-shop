from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^login/$', views.login_view, name='login'),
    re_path(r'^logout/$', views.logout_view, name='logout'),
    re_path(r'^register/$', views.register_view, name='register'),

    re_path(r'^profile/$', views.profile_view, name='profile'),

    re_path(r'^staff/create/$', views.staff_create_view, name='staff_create'),
    re_path(r'^staff/$', views.staff_list_view, name='staff_list'),

    # Client management (Admin & Staff)
    re_path(r'^clients/$', views.client_list_view, name='client_list'),
    re_path(r'^clients/(?P<client_id>\d+)/$', views.client_card_view, name='client_card'),
    re_path(r'^my-clients/$', views.my_clients_view, name='my_clients'),
    re_path(r'^my-clients/remove/(?P<client_id>\d+)/$', views.client_remove_view, name='client_remove'),
]
