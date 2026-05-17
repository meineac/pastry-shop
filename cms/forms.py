from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text', 'tags']
        widgets = {
            'rating': forms.Select(attrs={'required': True}),
            'review_text': forms.Textarea(attrs={'required': True, 'minlength': 1}),
            'tags': forms.SelectMultiple(attrs={'required': False})
        }
from .models import CompanyInfo, News, Vacancy, QaA
from purchasing.models import PromoCode

class CompanyInfoForm(forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = ['text_information', 'history_by_years', 'company_details', 'is_hidden']

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'image', 'short_summary', 'full_text', 'tags', 'is_hidden']
        widgets = {
            'tags': forms.SelectMultiple(attrs={'required': False})
        }

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'tags', 'is_hidden']
        widgets = {
            'tags': forms.SelectMultiple(attrs={'required': False})
        }

class QaAForm(forms.ModelForm):
    class Meta:
        model = QaA
        fields = ['question_text', 'answer_text', 'tags', 'is_hidden']
        widgets = {
            'tags': forms.SelectMultiple(attrs={'required': False})
        }

class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = ['code', 'expiration_date', 'status', 'conditions_of_application', 'is_hidden']
        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date', 'required': True})
        }
