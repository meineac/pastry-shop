from django.contrib import admin
from .models import PickupPoint, PromoCode, Order, OrderItem, Cart, CartItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ('address', 'price', 'working_hours', 'created_at', 'updated_at')
    search_fields = ('address',)

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'status', 'is_hidden', 'expiration_date', 'created_at', 'updated_at')
    list_filter = ('status', 'is_hidden')
    search_fields = ('code',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'delivery_type', 'delivery_price', 'status', 'payment_type', 'created_at', 'updated_at')
    list_filter = ('status', 'payment_type', 'delivery_type')
    search_fields = ('client__user__first_name', 'client__user__last_name', 'id', 'delivery_address')
    inlines = [OrderItemInline]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('client', 'created_at', 'updated_at')
    search_fields = ('client__user__first_name', 'client__user__last_name',)
    inlines = [CartItemInline]
