from django.db import models
from core.models import TimestampedModel
from users.models import User
from catalog.models import Product

class NewsTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class VacancyTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class QaATag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class ReviewTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name


class News(TimestampedModel):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    short_summary = models.TextField()
    full_text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(NewsTag, blank=True)

    def __str__(self):
        return self.title

class CompanyInfo(TimestampedModel):
    text_information = models.TextField()
    history_by_years = models.TextField()
    company_details = models.TextField()

    def __str__(self):
        return "Company Info"

class Vacancy(TimestampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(VacancyTag, blank=True)

    def __str__(self):
        return self.title

class QaA(TimestampedModel):
    question_text = models.TextField()
    answer_text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(QaATag, blank=True)

    def __str__(self):
        return self.question_text[:50]

class Review(TimestampedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(6)])
    review_text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews', help_text="Leave blank for a general store review")
    tags = models.ManyToManyField(ReviewTag, blank=True)

    def __str__(self):
        target = self.product.name if self.product else "General Store"
        return f"Review by {self.author.username} for {target} ({self.rating}/5)"
