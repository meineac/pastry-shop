from django import forms
from django.core.exceptions import FieldDoesNotExist
from .models import CompanyInfo, News, Vacancy, QaA, Review
from purchasing.models import PromoCode

class TagMixinForm(forms.ModelForm):
    tags_string = forms.CharField(
        max_length=255,
        required=False,
        help_text="Comma-separated list of tags."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and hasattr(self.instance, 'tags'):
            self.fields['tags_string'].initial = ", ".join([tag.name for tag in self.instance.tags.all()])
        
        try:
            tag_model = self._meta.model._meta.get_field('tags').related_model
            all_tags = tag_model.objects.values_list('name', flat=True)
            if all_tags:
                self.fields['tags_string'].help_text = f"Comma-separated list of tags. Currently available tags: {', '.join(all_tags)}"
            else:
                self.fields['tags_string'].help_text = "Comma-separated list of tags. No tags available yet."
        except FieldDoesNotExist:
            pass

    def save(self, commit=True):
        # We need to handle tags manually, even with commit=False
        instance = super().save(commit=False)
        
        # We must capture old tags before we replace them, but if commit=False, instance is not saved yet.
        # But if instance.pk exists, we can get them.
        old_tags = []
        if instance.pk and hasattr(instance, 'tags'):
            old_tags = list(instance.tags.all())

        def save_tags():
            tags_str = self.cleaned_data.get('tags_string', '')
            tag_names = [name.strip() for name in tags_str.split(',') if name.strip()]
            tag_model = self._meta.model._meta.get_field('tags').related_model
            
            current_tags = []
            for name in tag_names:
                tag, created = tag_model.objects.get_or_create(name=name)
                current_tags.append(tag)
            
            instance.tags.set(current_tags)

            # Cleanup orphaned tags
            try:
                accessor_name = self._meta.model._meta.get_field('tags').remote_field.get_accessor_name()
            except FieldDoesNotExist:
                accessor_name = None

            if accessor_name:
                removed_tags = [tag for tag in old_tags if tag not in current_tags]
                for tag in removed_tags:
                    related_manager = getattr(tag, accessor_name, None)
                    if related_manager is not None and not related_manager.exists():
                        tag.delete()

        if commit:
            instance.save()
            self.save_m2m() # for any other m2m fields
            save_tags()
        else:
            old_save_m2m = self.save_m2m
            def custom_save_m2m():
                old_save_m2m()
                save_tags()
            self.save_m2m = custom_save_m2m

        return instance


class CompanyInfoForm(forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = ['text_information', 'history_by_years', 'company_details',
                  'logo', 'video_url', 'certificate_text', 'is_hidden']

class NewsForm(TagMixinForm):
    class Meta:
        model = News
        fields = ['title', 'image', 'short_summary', 'full_text', 'is_hidden']

class VacancyForm(TagMixinForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'is_hidden']

class QaAForm(TagMixinForm):
    class Meta:
        model = QaA
        fields = ['question_text', 'answer_text', 'is_hidden']

class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = [
            'code', 'expiration_date', 'status',
            'discount_percentage', 'minimum_purchase_amount',
            'conditions_of_application', 'is_hidden',
        ]
        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date', 'required': True})
        }

class ReviewForm(TagMixinForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(attrs={'required': True}),
            'review_text': forms.Textarea(attrs={'required': True, 'minlength': 1}),
        }
