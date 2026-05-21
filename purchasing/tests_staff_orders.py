from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from users.models import CustomerProfile, StaffProfile
from purchasing.models import Order, OrderItem
from catalog.models import Product, Category, Manufacturer
from datetime import date

User = get_user_model()


class StaffOrdersTests(TestCase):
    def setUp(self):
        # Create user accounts
        self.staff_user = User.objects.create_user(username='staff', role=User.Role.STAFF, password='pwd')
        StaffProfile.objects.create(user=self.staff_user, position='Chef', date_of_birth=date(1990, 1, 1), contact_details='N/A')

        self.admin_user = User.objects.create_user(username='admin', role=User.Role.ADMIN, password='pwd')
        StaffProfile.objects.create(user=self.admin_user, position='Manager', date_of_birth=date(1985, 1, 1), contact_details='N/A')

        self.customer_user = User.objects.create_user(username='customer', role=User.Role.CUSTOMER, password='pwd')
        self.customer_profile = CustomerProfile.objects.create(user=self.customer_user, date_of_birth=date(2000, 1, 1), phone_number='+375 (29) 111-11-11')

        # Create product
        cat = Category.objects.create(name='Test Category')
        mfr = Manufacturer.objects.create(name='Test Manufacturer')
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.00'),
            quantity=10,
            category=cat,
            manufacturer=mfr
        )

        # Create orders in various states
        self.order_ready = self._create_order(Order.OrderStatus.READY)
        self.order_pending = self._create_order(Order.OrderStatus.PENDING)
        self.order_processing = self._create_order(Order.OrderStatus.PROCESSING)
        self.order_completed = self._create_order(Order.OrderStatus.COMPLETED)
        self.order_cancelled = self._create_order(Order.OrderStatus.CANCELLED)

    def _create_order(self, status):
        order = Order.objects.create(
            client=self.customer_profile,
            payment_type=Order.PaymentType.CASH,
            status=status,
            final_price=Decimal('10.00')
        )
        # We assume initial stock deduction has happened.
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            purchase_price=Decimal('10.00')
        )
        return order

    def test_active_orders_view_access(self):
        # Unauthenticated redirects to login
        response = self.client.get(reverse('purchasing:active_orders'))
        self.assertRedirects(response, reverse('login'))

        # Customer gets 403
        self.client.force_login(self.customer_user)
        response = self.client.get(reverse('purchasing:active_orders'))
        self.assertEqual(response.status_code, 403)

        # Staff can access
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('purchasing:active_orders'))
        self.assertEqual(response.status_code, 200)

        # Admin can access
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('purchasing:active_orders'))
        self.assertEqual(response.status_code, 200)

    def test_active_orders_sorting(self):
        """Test that orders are sorted READY -> PROCESSING -> PENDING, then by created_at."""
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('purchasing:active_orders'))
        
        orders = list(response.context['orders'])
        # We expect only active orders to be returned: READY, PROCESSING, PENDING
        self.assertEqual(len(orders), 3)
        self.assertEqual(orders[0].status, Order.OrderStatus.READY)
        self.assertEqual(orders[1].status, Order.OrderStatus.PROCESSING)
        self.assertEqual(orders[2].status, Order.OrderStatus.PENDING)

    def test_update_order_status(self):
        self.client.force_login(self.staff_user)
        
        # Change PENDING to PROCESSING
        response = self.client.post(
            reverse('purchasing:update_order_status', args=[self.order_pending.id]),
            {'new_status': Order.OrderStatus.PROCESSING}
        )
        # Should redirect back to active_orders by default
        self.assertRedirects(response, reverse('purchasing:active_orders'))
        self.order_pending.refresh_from_db()
        self.assertEqual(self.order_pending.status, Order.OrderStatus.PROCESSING)

    def test_cancel_order_restores_stock(self):
        """Cancelling an order should restore the product stock."""
        initial_quantity = self.product.quantity
        order_qty = self.order_ready.items.first().quantity

        self.client.force_login(self.staff_user)
        response = self.client.post(
            reverse('purchasing:update_order_status', args=[self.order_ready.id]),
            {'new_status': Order.OrderStatus.CANCELLED}
        )
        
        self.order_ready.refresh_from_db()
        self.assertEqual(self.order_ready.status, Order.OrderStatus.CANCELLED)

        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity + order_qty)

    def test_cannot_update_completed_or_cancelled_order(self):
        self.client.force_login(self.staff_user)
        
        # Try to change COMPLETED order
        self.client.post(
            reverse('purchasing:update_order_status', args=[self.order_completed.id]),
            {'new_status': Order.OrderStatus.READY}
        )
        self.order_completed.refresh_from_db()
        self.assertEqual(self.order_completed.status, Order.OrderStatus.COMPLETED)

        # Try to change CANCELLED order
        self.client.post(
            reverse('purchasing:update_order_status', args=[self.order_cancelled.id]),
            {'new_status': Order.OrderStatus.READY}
        )
        self.order_cancelled.refresh_from_db()
        self.assertEqual(self.order_cancelled.status, Order.OrderStatus.CANCELLED)
