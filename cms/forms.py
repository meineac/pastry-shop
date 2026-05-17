from django import forms
from .models import Review

from core.models import Tag

from .models import CompanyInfo, News, Vacancy, QaA
from purchasing.models import PromoCode

class TagMixinForm(forms.ModelForm):
    new_tags = forms.CharField(
        max_length=255,
        required=False,
        help_text="Comma-separated list of new tags to create and attach."
    )

    def save(self, commit=True):
        # Capture old tags if the instance already exists
        old_tags = []
        if self.instance.pk and hasattr(self.instance, 'tags'):
            old_tags = list(self.instance.tags.all())

        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
            self.save_new_tags(instance)
            self.cleanup_orphaned_tags(old_tags, instance)
        return instance

    def save_new_tags(self, instance):
        new_tags_str = self.cleaned_data.get('new_tags', '')
        if new_tags_str:
            tag_names = [name.strip() for name in new_tags_str.split(',') if name.strip()]
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                instance.tags.add(tag)

    def cleanup_orphaned_tags(self, old_tags, instance):
        # Determine which tags were removed
        current_tags = list(instance.tags.all())
        removed_tags = [tag for tag in old_tags if tag not in current_tags]

        # Check and delete orphaned tags
        for tag in removed_tags:
            is_orphaned = True
            for related_object in tag._meta.related_objects:
                accessor_name = related_object.get_accessor_name()
                related_manager = getattr(tag, accessor_name, None)
                if related_manager and related_manager.exists():
                    is_orphaned = False
                    break

            if is_orphaned:
                tag.delete()


class CompanyInfoForm(forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = ['text_information', 'history_by_years', 'company_details', 'is_hidden']

class NewsForm(TagMixinForm):
    class Meta:
        model = News
        fields = ['title', 'image', 'short_summary', 'full_text', 'tags', 'new_tags', 'is_hidden']
        widgets = {
            'tags': forms.SelectMultiple(attrs={'required': False})
        }

class VacancyForm(TagMixinForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'tags', 'new_tags', 'is_hidden']
        widgets = {
            'tags': forms.SelectMultiple(attrs={'required': False})
        }

class QaAForm(TagMixinForm):
    class Meta:
        model = QaA
        fields = ['question_text', 'answer_text', 'tags', 'new_tags', 'is_hidden']
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

class ReviewForm(TagMixinForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text', 'tags', 'new_tags']
        widgets = {
            'rating': forms.Select(attrs={'required': True}),
            'review_text': forms.Textarea(attrs={'required': True, 'minlength': 1}),
            'tags': forms.SelectMultiple(attrs={'required': False})
        }
