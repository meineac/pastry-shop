from django.contrib import admin
from .models import Category, Manufacturer, Product

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = [ProductInline]

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'created_at')
    search_fields = ('name', 'contact_email')
    inlines = [ProductInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'manufacturer', 'price', 'quantity', 'unit_of_measurement')
    list_filter = ('category', 'manufacturer', 'unit_of_measurement')
    search_fields = ('name', 'category__name', 'manufacturer__name')
