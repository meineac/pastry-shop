from django.test import TestCase, Client
from django.urls import reverse
from .models import News, CompanyInfo, Vacancy, QaA, Review, NewsTag
from users.models import User, CustomerProfile
from datetime import date

class CMSViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123', role=User.Role.CUSTOMER)
        self.customer = CustomerProfile.objects.create(
            user=self.user,
            date_of_birth=date(1990, 1, 1),
            phone_number='+375 (29) 111-22-33'
        )

        self.tag = NewsTag.objects.create(name='Test Tag')
        self.news = News.objects.create(
            title='Test News',
            short_summary='Short',
            full_text='Full Text'
        )
        self.news.tags.add(self.tag)

        self.company_info = CompanyInfo.objects.create(
            text_information='Info',
            history_by_years='History',
            company_details='Details'
        )

    def test_home_view(self):
        response = self.client.get(reverse('cms:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test News')

    def test_about_company_view(self):
        response = self.client.get(reverse('cms:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Details')

    def test_news_list_view(self):
        response = self.client.get(reverse('cms:news_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test News')

        # Test search
        response = self.client.get(reverse('cms:news_list'), {'q': 'Test News'})
        self.assertContains(response, 'Test News')

    def test_reviews_list_view(self):
        response = self.client.get(reverse('cms:reviews'))
        self.assertEqual(response.status_code, 200)

    def test_review_create_view_unauthenticated(self):
        response = self.client.get(reverse('cms:review_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_review_create_view_authenticated(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('cms:review_create'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('cms:review_create'), {
            'rating': 5,
            'review_text': 'Great store!'
        })
        self.assertRedirects(response, reverse('cms:reviews'))
        self.assertTrue(Review.objects.filter(author=self.user, rating=5).exists())
