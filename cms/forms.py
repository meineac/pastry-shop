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
