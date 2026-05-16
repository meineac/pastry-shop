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
    list_display = ('address', 'working_hours', 'created_at', 'updated_at')
    search_fields = ('address',)

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'status', 'expiration_date', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('code',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'delivery_type', 'payment_type', 'created_at', 'updated_at')
    list_filter = ('status', 'delivery_type', 'payment_type')
    search_fields = ('client__user__first_name', 'client__user__last_name', 'id')
    inlines = [OrderItemInline]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('client', 'created_at', 'updated_at')
    search_fields = ('client__user__first_name', 'client__user__last_name',)
    inlines = [CartItemInline]
