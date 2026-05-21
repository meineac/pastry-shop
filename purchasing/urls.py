from django.urls import re_path
from . import views

app_name = 'purchasing'

urlpatterns = [
    re_path(r'^cart/$', views.cart_view, name='cart'),
    re_path(r'^cart/add/(?P<product_id>\d+)/$', views.add_to_cart_view, name='add_to_cart'),
    re_path(r'^cart/remove/(?P<cart_item_id>\d+)/$', views.remove_from_cart_view, name='remove_from_cart'),
    re_path(r'^checkout/$', views.checkout_view, name='checkout'),
    re_path(r'^checkout/apply-promo/$', views.apply_promo_view, name='apply_promo'),
    re_path(r'^checkout/place-order/$', views.place_order_view, name='place_order'),
    re_path(r'^profile/orders/$', views.order_history_view, name='order_history'),
    re_path(r'^profile/orders/(?P<order_id>\d+)/$', views.order_details_view, name='order_details'),
]
