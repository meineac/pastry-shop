from django.contrib import admin
from .models import NewsTag, VacancyTag, QaATag, ReviewTag, News, CompanyInfo, Vacancy, QaA, Review

admin.site.register(NewsTag)
admin.site.register(VacancyTag)
admin.site.register(QaATag)
admin.site.register(ReviewTag)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    filter_horizontal = ('tags',)

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at')

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    filter_horizontal = ('tags',)

@admin.register(QaA)
class QaAAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at')
    search_fields = ('question_text',)
    filter_horizontal = ('tags',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'product', 'created_at')
    list_filter = ('rating',)
    search_fields = ('author__username', 'product__name')
    filter_horizontal = ('tags',)
