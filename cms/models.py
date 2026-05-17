from django.db import models
from core.models import TimestampedModel, Tag
from users.models import User
from catalog.models import Product


class TagCleanupMixin(models.Model):
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        # Capture tags before deletion
        tags_to_check = []
        if hasattr(self, 'tags'):
            tags_to_check = list(self.tags.all())

        result = super().delete(*args, **kwargs)

        # Check if tags are orphaned
        for tag in tags_to_check:
            is_orphaned = True
            for related_object in tag._meta.related_objects:
                accessor_name = related_object.get_accessor_name()
                related_manager = getattr(tag, accessor_name, None)
                if related_manager and related_manager.exists():
                    is_orphaned = False
                    break

            if is_orphaned:
                tag.delete()

        return result



class News(TagCleanupMixin, TimestampedModel):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    short_summary = models.TextField()
    full_text = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, related_name='news_articles')
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class CompanyInfo(TimestampedModel):
    text_information = models.TextField()
    history_by_years = models.TextField()
    company_details = models.TextField()
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return "Company Info"

class Vacancy(TagCleanupMixin, TimestampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, related_name='vacancies')
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class QaA(TagCleanupMixin, TimestampedModel):
    question_text = models.TextField()
    answer_text = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, related_name='qnas')
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text[:50]

class Review(TagCleanupMixin, TimestampedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(6)])
    review_text = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews', help_text="Leave blank for a general store review")
    tags = models.ManyToManyField(Tag, blank=True, related_name='reviews')

    def __str__(self):
        target = self.product.name if self.product else "General Store"
        return f"Review by {self.author.username} for {target} ({self.rating}/5)"
