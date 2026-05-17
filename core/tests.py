from django.test import TestCase
from cms.models import News, Vacancy, NewsTag

from cms.forms import NewsForm

class TagCleanupTests(TestCase):
    def test_orphaned_tag_cleanup_on_form_save(self):
        tag = NewsTag.objects.create(name='test_tag')
        news1 = News.objects.create(title='News 1', short_summary='Sum 1', full_text='Text 1')
        news2 = News.objects.create(title='News 2', short_summary='Sum 2', full_text='Text 2')

        news1.tags.add(tag)
        news2.tags.add(tag)

        self.assertEqual(NewsTag.objects.count(), 1)

        # Simulate removing the tag from news1 via form
        form_data_1 = {
            'title': 'News 1',
            'short_summary': 'Sum 1',
            'full_text': 'Text 1',
            'tags': [],
            'new_tags': ''
        }
        form1 = NewsForm(data=form_data_1, instance=news1)
        self.assertTrue(form1.is_valid())
        form1.save()
        self.assertEqual(NewsTag.objects.count(), 1) # Still attached to news2

        # Simulate removing the tag from news2 via form
        form_data_2 = {
            'title': 'News 2',
            'short_summary': 'Sum 2',
            'full_text': 'Text 2',
            'tags': [],
            'new_tags': ''
        }
        form2 = NewsForm(data=form_data_2, instance=news2)
        self.assertTrue(form2.is_valid())
        form2.save()
        self.assertEqual(NewsTag.objects.count(), 0) # Now orphaned and deleted

    def test_orphaned_tag_cleanup_on_instance_delete(self):
        tag = NewsTag.objects.create(name='test_tag')
        news1 = News.objects.create(title='News 1')
        news1.tags.add(tag)

        self.assertEqual(NewsTag.objects.count(), 1)

        news1.delete()
        self.assertEqual(NewsTag.objects.count(), 0) # Orphaned via deletion
