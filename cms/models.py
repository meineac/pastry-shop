from django.core.exceptions import FieldDoesNotExist
from django.db import models
from core.models import TimestampedModel
from users.models import User
from catalog.models import Product


class TagCleanupMixin(models.Model):
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        tags_to_check = list(self.tags.all()) if hasattr(self, 'tags') else []
        
        try:
            accessor_name = self._meta.get_field('tags').remote_field.get_accessor_name()
        except FieldDoesNotExist:
            accessor_name = None

        result = super().delete(*args, **kwargs)

        for tag in tags_to_check:
            if accessor_name:
                related_manager = getattr(tag, accessor_name, None)
                if related_manager is not None and not related_manager.exists():
                    tag.delete()

        return result


class AbstractTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

    class Meta:
        abstract = True

class NewsTag(AbstractTag):
    pass

class VacancyTag(AbstractTag):
    pass

class QaATag(AbstractTag):
    pass

class ReviewTag(AbstractTag):
    pass


class News(TagCleanupMixin, TimestampedModel):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    short_summary = models.TextField()
    full_text = models.TextField()
    tags = models.ManyToManyField(NewsTag, blank=True, related_name='news_articles')
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class CompanyInfo(TimestampedModel):
    text_information = models.TextField()
    history_by_years = models.TextField()
    company_details = models.TextField()
    logo = models.ImageField(upload_to='company/', null=True, blank=True)
    video_url = models.URLField(blank=True, help_text="URL to an embeddable video (YouTube embed URL).")
    certificate_text = models.TextField(blank=True, help_text="Plain text certificate — must not be styled.")
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return "Company Info"


class Partner(TimestampedModel):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='partners/', null=True, blank=True)
    website_url = models.URLField()
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class PromotionalBanner(TimestampedModel):
    title = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='banners/')
    link_url = models.URLField(blank=True)
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title or f"Banner #{self.id}"

class Vacancy(TagCleanupMixin, TimestampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.ManyToManyField(VacancyTag, blank=True, related_name='vacancies')
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class QaA(TagCleanupMixin, TimestampedModel):
    question_text = models.TextField()
    answer_text = models.TextField()
    tags = models.ManyToManyField(QaATag, blank=True, related_name='qnas')
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text[:50]

class Review(TagCleanupMixin, TimestampedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(6)])
    review_text = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews', help_text="Leave blank for a general store review")
    tags = models.ManyToManyField(ReviewTag, blank=True, related_name='reviews')

    def __str__(self):
        target = self.product.name if self.product else "General Store"
        return f"Review by {self.author.username} for {target} ({self.rating}/5)"
