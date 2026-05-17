from django.test import TestCase
from core.models import Tag
from cms.models import News, Vacancy

class TagCleanupTests(TestCase):
    def test_orphaned_tag_cleanup_on_m2m_remove(self):
        tag = Tag.objects.create(name='test_tag')
        news1 = News.objects.create(title='News 1')
        news2 = News.objects.create(title='News 2')

        news1.tags.add(tag)
        news2.tags.add(tag)

        self.assertEqual(Tag.objects.count(), 1)

        news1.tags.remove(tag)
        self.assertEqual(Tag.objects.count(), 1) # Still attached to news2

        news2.tags.remove(tag)
        self.assertEqual(Tag.objects.count(), 0) # Now orphaned and deleted

    def test_orphaned_tag_cleanup_on_instance_delete(self):
        tag = Tag.objects.create(name='test_tag')
        news1 = News.objects.create(title='News 1')
        news1.tags.add(tag)

        self.assertEqual(Tag.objects.count(), 1)

        news1.delete()
        self.assertEqual(Tag.objects.count(), 0) # Orphaned via deletion
