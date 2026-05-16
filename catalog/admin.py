from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Manufacturer, Product

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    inlines = [ProductInline]

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'contact_email', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'contact_email')
    inlines = [ProductInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'price', 'quantity', 'unit_of_measurement', 'image_preview',
        'ingredients', 'category', 'manufacturer', 'created_at', 'updated_at'
    )
    list_filter = ('category', 'manufacturer', 'unit_of_measurement')
    search_fields = ('name', 'ingredients', 'category__name', 'manufacturer__name')
    ordering = ('name', 'price', 'category', 'manufacturer')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.photo.url)
        return "No Image"
    image_preview.short_description = "Image Preview"
