from django.test import TestCase, Client
from django.urls import reverse
from .models import News, CompanyInfo, Vacancy, QaA, Review, NewsTag
from users.models import User, CustomerProfile
from catalog.models import Product, Category, Manufacturer
from purchasing.models import Order, OrderItem
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

    def test_product_review_eligibility(self):
        # Create catalog items
        cat = Category.objects.create(name="Cakes")
        man = Manufacturer.objects.create(name="Sweet Bakers")
        product = Product.objects.create(
            name="Chocolate Cake",
            category=cat,
            manufacturer=man,
            price=25.00,
            quantity=10,
            ingredients="ingredients"
        )
        
        self.client.login(username='testuser', password='password123')
        
        # Case 1: Try to review product without purchasing it
        response = self.client.get(reverse('cms:review_create') + f"?product_id={product.id}")
        self.assertEqual(response.status_code, 302) # Redirect to product details
        self.assertRedirects(response, reverse('catalog:product_detail', kwargs={'product_id': product.id}))
        
        # Case 2: User purchases product but order is not COMPLETED (still PENDING)
        order = Order.objects.create(
            client=self.customer,
            delivery_type=Order.DeliveryType.PICKUP,
            payment_type=Order.PaymentType.CASH,
            status=Order.OrderStatus.PENDING,
            final_price=25.00
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            purchase_price=25.00,
            historical_product_name=product.name
        )
        
        response = self.client.get(reverse('cms:review_create') + f"?product_id={product.id}")
        self.assertEqual(response.status_code, 302)
        
        # Case 3: Order is COMPLETED -> User can access review page and leave a review
        order.status = Order.OrderStatus.COMPLETED
        order.save()
        
        response = self.client.get(reverse('cms:review_create') + f"?product_id={product.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Leave a Review for {product.name}")
        
        # Post a valid review
        response = self.client.post(reverse('cms:review_create') + f"?product_id={product.id}", {
            'rating': 4,
            'review_text': 'Tastes very good!'
        })
        self.assertRedirects(response, reverse('catalog:product_detail', kwargs={'product_id': product.id}))
        self.assertTrue(Review.objects.filter(author=self.user, product=product, rating=4).exists())
        
        # Case 4: Try to leave a review again for the same product -> Redirected/Denied
        response = self.client.get(reverse('cms:review_create') + f"?product_id={product.id}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('catalog:product_detail', kwargs={'product_id': product.id}))

    def test_admin_and_staff_cannot_create_edit_delete_reviews(self):
        # Create users
        admin_user = User.objects.create_user(username='admin_user', password='password123', role=User.Role.ADMIN)
        staff_user = User.objects.create_user(username='staff_user', password='password123', role=User.Role.STAFF)
        
        # Create a customer's review to test editing/deleting
        customer_review = Review.objects.create(
            author=self.user,
            rating=5,
            review_text="Lovely!"
        )

        for test_user in [admin_user, staff_user]:
            self.client.login(username=test_user.username, password='password123')

            # 1. Access review creation page (GET) should yield 403 PermissionDenied
            response = self.client.get(reverse('cms:review_create'))
            self.assertEqual(response.status_code, 403)

            # 2. Submit review creation (POST) should yield 403 PermissionDenied
            response = self.client.post(reverse('cms:review_create'), {'rating': 5, 'review_text': 'Nice'})
            self.assertEqual(response.status_code, 403)

            # 3. Access review edit page (GET) should yield 403 PermissionDenied
            response = self.client.get(reverse('cms:review_edit', kwargs={'pk': customer_review.id}))
            self.assertEqual(response.status_code, 403)

            # 4. Access review delete page (GET) should yield 403 PermissionDenied
            response = self.client.get(reverse('cms:review_delete', kwargs={'pk': customer_review.id}))
            self.assertEqual(response.status_code, 403)

            self.client.logout()

