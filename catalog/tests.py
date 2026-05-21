from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
import decimal

from users.models import User, CustomerProfile
from catalog.models import Product, Category, Manufacturer

class CatalogCRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Setup categories and manufacturers
        self.category = Category.objects.create(name="Pastries", description="Delicious pastries")
        self.manufacturer = Manufacturer.objects.create(name="Local Bakery", description="Our baking partner")

        # Create active and inactive products
        self.active_product = Product.objects.create(
            name="Croissant",
            price=decimal.Decimal("2.50"),
            quantity=15,
            unit_of_measurement=Product.UnitMeasurement.PIECES,
            ingredients="Butter, flour, sugar",
            is_active=True,
            category=self.category,
            manufacturer=self.manufacturer
        )
        self.inactive_product = Product.objects.create(
            name="Deactivated Cake",
            price=decimal.Decimal("15.00"),
            quantity=2,
            unit_of_measurement=Product.UnitMeasurement.PIECES,
            ingredients="Flour, sugar, cocoa",
            is_active=False,
            category=self.category,
            manufacturer=self.manufacturer
        )

        # Create users of different roles
        self.admin = User.objects.create_user(username="admin", password="password123", role=User.Role.ADMIN)
        self.customer = User.objects.create_user(username="customer", password="password123", role=User.Role.CUSTOMER)
        self.customer_profile = CustomerProfile.objects.create(
            user=self.customer,
            date_of_birth=date(1990, 1, 1),
            phone_number="+375 (29) 111-11-11"
        )

    def test_admin_can_create_product(self):
        self.client.login(username="admin", password="password123")
        
        create_data = {
            'name': 'New Muffin',
            'price': '3.20',
            'quantity': 20,
            'unit_of_measurement': Product.UnitMeasurement.PIECES,
            'ingredients': 'Flour, sugar, blueberries',
            'is_active': True,
            'category': self.category.id,
            'manufacturer': self.manufacturer.id
        }
        
        # Access create view (GET)
        response = self.client.get(reverse('catalog:product_create'))
        self.assertEqual(response.status_code, 200)

        # Submit create form (POST)
        response = self.client.post(reverse('catalog:product_create'), create_data)
        # Should redirect to details page
        new_product = Product.objects.get(name="New Muffin")
        self.assertRedirects(response, reverse('catalog:product_detail', args=[new_product.id]))

    def test_admin_can_edit_product(self):
        self.client.login(username="admin", password="password123")

        # Access edit view (GET)
        response = self.client.get(reverse('catalog:product_edit', args=[self.active_product.id]))
        self.assertEqual(response.status_code, 200)

        edit_data = {
            'name': 'Updated Croissant',
            'price': '2.99',
            'quantity': 10,
            'unit_of_measurement': Product.UnitMeasurement.PIECES,
            'ingredients': 'Extra butter, flour, sugar',
            'is_active': False,  # Turn inactive
            'category': self.category.id,
            'manufacturer': self.manufacturer.id
        }

        # Submit edit form (POST)
        response = self.client.post(reverse('catalog:product_edit', args=[self.active_product.id]), edit_data)
        self.assertRedirects(response, reverse('catalog:product_detail', args=[self.active_product.id]))
        
        self.active_product.refresh_from_db()
        self.assertEqual(self.active_product.name, 'Updated Croissant')
        self.assertEqual(self.active_product.price, decimal.Decimal('2.99'))
        self.assertFalse(self.active_product.is_active)

    def test_admin_can_delete_product(self):
        self.client.login(username="admin", password="password123")

        # Access delete confirmation view (GET)
        response = self.client.get(reverse('catalog:product_delete', args=[self.active_product.id]))
        self.assertEqual(response.status_code, 200)

        # Perform deletion (POST)
        response = self.client.post(reverse('catalog:product_delete', args=[self.active_product.id]))
        self.assertRedirects(response, reverse('catalog:product_list'))
        
        self.assertFalse(Product.objects.filter(id=self.active_product.id).exists())

    def test_non_admin_cannot_access_crud(self):
        # 1. Anonymous guest should redirect to login
        response = self.client.get(reverse('catalog:product_create'))
        self.assertRedirects(response, reverse('login'))
        
        response = self.client.post(reverse('catalog:product_create'), {})
        self.assertRedirects(response, reverse('login'))

        # 2. Authenticated Customer should be Forbidden (403 PermissionDenied)
        self.client.login(username="customer", password="password123")

        response = self.client.get(reverse('catalog:product_create'))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('catalog:product_create'), {})
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('catalog:product_edit', args=[self.active_product.id]))
        self.assertEqual(response.status_code, 403)

        response = self.client.get(reverse('catalog:product_delete', args=[self.active_product.id]))
        self.assertEqual(response.status_code, 403)

    def test_inactive_product_detail_view_permissions(self):
        # Inactive product: self.inactive_product
        
        # Guest gets 404
        response = self.client.get(reverse('catalog:product_detail', args=[self.inactive_product.id]))
        self.assertEqual(response.status_code, 404)

        # Customer gets 404
        self.client.login(username="customer", password="password123")
        response = self.client.get(reverse('catalog:product_detail', args=[self.inactive_product.id]))
        self.assertEqual(response.status_code, 404)

        # Admin gets 200
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse('catalog:product_detail', args=[self.inactive_product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.inactive_product.name)

    def test_deactivated_products_excluded_from_customer_search_and_list(self):
        # Guest or Customer lists catalog
        response = self.client.get(reverse('catalog:product_list'))
        self.assertContains(response, self.active_product.name)
        self.assertNotContains(response, self.inactive_product.name)

        # Guest or Customer searches catalog
        response = self.client.get(reverse('catalog:product_list'), {'q': 'Deactivated'})
        self.assertNotContains(response, self.inactive_product.name)
        self.assertNotContains(response, self.active_product.name)

        # Admin list includes all products
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse('catalog:product_list'))
        self.assertContains(response, self.active_product.name)
        self.assertContains(response, self.inactive_product.name)
