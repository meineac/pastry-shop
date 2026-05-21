from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^login/$', views.login_view, name='login'),
    re_path(r'^logout/$', views.logout_view, name='logout'),
    re_path(r'^register/$', views.register_view, name='register'),

    re_path(r'^profile/$', views.profile_view, name='profile'),

    re_path(r'^staff/$', views.staff_list_view, name='staff_list'),
]
