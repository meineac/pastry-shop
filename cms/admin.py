from django.contrib import admin
from django.utils.html import format_html
from .models import News, CompanyInfo, Vacancy, QaA, Review, NewsTag, VacancyTag, QaATag, ReviewTag

admin.site.register(NewsTag)
admin.site.register(VacancyTag)
admin.site.register(QaATag)
admin.site.register(ReviewTag)

class DisplayTagsMixin:
    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = "Tags"

@admin.register(News)
class NewsAdmin(admin.ModelAdmin, DisplayTagsMixin):
    list_display = ('title', 'image_preview', 'display_tags', 'is_hidden', 'short_summary', 'created_at', 'updated_at')
    search_fields = ('title', 'tags__name', 'short_summary')
    list_filter = ('is_hidden', 'tags')
    ordering = ('created_at', 'title')
    filter_horizontal = ('tags',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image Preview"

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_hidden', 'created_at', 'updated_at')
    list_filter = ('is_hidden',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin, DisplayTagsMixin):
    list_display = ('title', 'description', 'display_tags', 'is_hidden', 'created_at', 'updated_at')
    search_fields = ('title', 'tags__name', 'description')
    ordering = ('created_at', 'updated_at', 'title')
    list_filter = ('is_hidden', 'tags')
    filter_horizontal = ('tags',)

@admin.register(QaA)
class QaAAdmin(admin.ModelAdmin, DisplayTagsMixin):
    list_display = ('question_text', 'answer_text', 'display_tags', 'is_hidden', 'created_at', 'updated_at')
    search_fields = ('question_text', 'tags__name', 'answer_text')
    ordering = ('created_at', 'updated_at')
    list_filter = ('is_hidden', 'tags')
    filter_horizontal = ('tags',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin, DisplayTagsMixin):
    list_display = ('product', 'author', 'rating', 'review_text', 'display_tags', 'created_at', 'updated_at')
    search_fields = ('product__name', 'author__username')
    ordering = ('rating', 'created_at', 'updated_at')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
