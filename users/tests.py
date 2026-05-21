from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Manufacturer, Product
from purchasing.models import Order, OrderItem
from users.models import CustomerProfile, StaffProfile

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_customer(username='customer1', dob=None):
    """Create a User with CUSTOMER role and a CustomerProfile."""
    if dob is None:
        dob = date(1990, 1, 1)
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='testpassword123',
        role=User.Role.CUSTOMER,
    )
    profile = CustomerProfile.objects.create(
        user=user,
        date_of_birth=dob,
        phone_number='+375 (29) 123-45-67',
    )
    return user, profile


def make_staff(username='staffmember'):
    """Create a User with STAFF role and a StaffProfile."""
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='testpassword123',
        role=User.Role.STAFF,
    )
    profile = StaffProfile.objects.create(
        user=user,
        position='Pastry Chef',
        contact_details='ext. 101',
        date_of_birth=date(1985, 6, 15),
    )
    return user, profile


def make_admin(username='adminuser'):
    """Create a User with ADMIN role and a StaffProfile."""
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='testpassword123',
        role=User.Role.ADMIN,
    )
    profile = StaffProfile.objects.create(
        user=user,
        position='Manager',
        contact_details='ext. 001',
        date_of_birth=date(1980, 3, 20),
    )
    return user, profile


def make_product(name='Test Cake', price='10.00'):
    """Create a minimal Product."""
    cat = Category.objects.create(name=f'Cat-{name}')
    mfr = Manufacturer.objects.create(name=f'Mfr-{name}')
    return Product.objects.create(
        name=name,
        price=price,
        quantity=100,
        ingredients='Flour, Sugar',
        category=cat,
        manufacturer=mfr,
    )


# ---------------------------------------------------------------------------
# Existing role constraint tests (unchanged)
# ---------------------------------------------------------------------------

class UserRoleConstraintsTests(TestCase):
    def test_superuser_is_always_admin_and_staff(self):
        user = User.objects.create_superuser(
            username="super_admin",
            email="super@example.com",
            password="password123"
        )
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

        user2 = User.objects.create_user(
            username="staff_user",
            email="staff@example.com",
            password="password123",
            role=User.Role.STAFF
        )
        user2.is_superuser = True
        user2.save()
        self.assertEqual(user2.role, User.Role.STAFF)
        self.assertFalse(user2.is_superuser)
        self.assertTrue(user2.is_staff)

    def test_admin_is_not_always_superuser(self):
        admin_user = User.objects.create_user(
            username="normal_admin",
            email="admin@example.com",
            password="password123",
            role=User.Role.ADMIN
        )
        self.assertEqual(admin_user.role, User.Role.ADMIN)
        self.assertTrue(admin_user.is_staff)
        self.assertFalse(admin_user.is_superuser)

    def test_staff_is_never_superuser(self):
        staff_user = User.objects.create_user(
            username="just_staff",
            email="staff2@example.com",
            password="password123",
            role=User.Role.STAFF
        )
        self.assertEqual(staff_user.role, User.Role.STAFF)
        self.assertFalse(staff_user.is_superuser)
        self.assertTrue(staff_user.is_staff)

        staff_user.is_superuser = True
        staff_user.save()
        self.assertFalse(staff_user.is_superuser)
        self.assertTrue(staff_user.is_staff)

    def test_customer_is_never_superuser_or_staff(self):
        customer = User.objects.create_user(
            username="normal_customer",
            email="cust@example.com",
            password="password123",
            role=User.Role.CUSTOMER
        )
        self.assertEqual(customer.role, User.Role.CUSTOMER)
        self.assertFalse(customer.is_superuser)
        self.assertFalse(customer.is_staff)

        customer.is_superuser = True
        customer.is_staff = True
        customer.save()
        self.assertFalse(customer.is_superuser)
        self.assertFalse(customer.is_staff)

    def test_clean_validation_errors(self):
        user = User(username="invalid_user", role=User.Role.STAFF, is_superuser=True)
        with self.assertRaises(ValidationError):
            user.clean()

        user2 = User(username="invalid_user2", role=User.Role.CUSTOMER, is_superuser=True)
        with self.assertRaises(ValidationError):
            user2.clean()


# ---------------------------------------------------------------------------
# Client list view tests
# ---------------------------------------------------------------------------

class ClientListViewTests(TestCase):
    """Tests for /clients/ — requires ADMIN or STAFF role."""

    def setUp(self):
        self.staff_user, self.staff_profile = make_staff('cl_staff')
        self.customer_user, self.customer_profile = make_customer('cl_cust1')

    def test_customer_cannot_access_client_list(self):
        self.client.force_login(self.customer_user)
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse('client_list'))
        self.assertRedirects(response, reverse('login'))

    def test_staff_can_access_client_list(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.customer_user.username)

    def test_search_by_name_filters_results(self):
        make_customer('other_cust')
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('client_list'), {'q': 'cl_cust1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cl_cust1')
        self.assertNotContains(response, 'other_cust')

    def test_add_client_to_my_list(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(
            reverse('client_list'),
            {'client_id': self.customer_profile.id},
        )
        self.assertRedirects(response, reverse('client_list'))
        self.assertIn(self.customer_profile, self.staff_profile.my_clients.all())

    def test_filter_by_category(self):
        """Clients who bought products in a given category should appear."""
        product = make_product('Eclair')
        # Create completed order for this customer
        order = Order.objects.create(
            client=self.customer_profile,
            payment_type=Order.PaymentType.CASH,
            status=Order.OrderStatus.COMPLETED,
            final_price='10.00',
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            purchase_price='10.00',
            historical_product_name=product.name,
        )
        self.client.force_login(self.staff_user)
        response = self.client.get(
            reverse('client_list'),
            {'category': product.category.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.customer_user.username)


# ---------------------------------------------------------------------------
# Client card view tests
# ---------------------------------------------------------------------------

class ClientCardViewTests(TestCase):
    """Tests for /clients/<id>/ — requires ADMIN or STAFF role."""

    def setUp(self):
        self.staff_user, self.staff_profile = make_staff('cc_staff')
        self.customer_user, self.customer_profile = make_customer('cc_cust')

    def test_staff_can_view_client_card(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(
            reverse('client_card', kwargs={'client_id': self.customer_profile.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.customer_user.username)

    def test_customer_cannot_view_client_card(self):
        self.client.force_login(self.customer_user)
        response = self.client.get(
            reverse('client_card', kwargs={'client_id': self.customer_profile.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_client_card_shows_age(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(
            reverse('client_card', kwargs={'client_id': self.customer_profile.id})
        )
        today = date.today()
        dob = self.customer_profile.date_of_birth
        expected_age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
        self.assertContains(response, str(expected_age))

    def test_client_card_shows_orders(self):
        order = Order.objects.create(
            client=self.customer_profile,
            payment_type=Order.PaymentType.CASH,
            status=Order.OrderStatus.COMPLETED,
            final_price='25.00',
        )
        self.client.force_login(self.staff_user)
        response = self.client.get(
            reverse('client_card', kwargs={'client_id': self.customer_profile.id})
        )
        self.assertContains(response, str(order.id))


# ---------------------------------------------------------------------------
# My Clients view tests
# ---------------------------------------------------------------------------

class MyClientsViewTests(TestCase):
    """Tests for /my-clients/ — requires ADMIN or STAFF role."""

    def setUp(self):
        self.staff_user, self.staff_profile = make_staff('mc_staff')
        self.customer_user, self.customer_profile = make_customer('mc_cust')

    def test_my_clients_empty_initially(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('my_clients'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your client list is empty')

    def test_my_clients_shows_added_client(self):
        self.staff_profile.my_clients.add(self.customer_profile)
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('my_clients'))
        self.assertContains(response, self.customer_user.username)

    def test_remove_client_from_my_list(self):
        self.staff_profile.my_clients.add(self.customer_profile)
        self.client.force_login(self.staff_user)
        response = self.client.post(
            reverse('client_remove', kwargs={'client_id': self.customer_profile.id})
        )
        self.assertRedirects(response, reverse('my_clients'))
        self.assertNotIn(self.customer_profile, self.staff_profile.my_clients.all())

    def test_customer_cannot_access_my_clients(self):
        self.client.force_login(self.customer_user)
        response = self.client.get(reverse('my_clients'))
        self.assertEqual(response.status_code, 403)


# ---------------------------------------------------------------------------
# Statistics view tests
# ---------------------------------------------------------------------------

class StatisticsViewTests(TestCase):
    """Tests for /statistics/ — requires ADMIN or STAFF role."""

    def setUp(self):
        self.staff_user, self.staff_profile = make_staff('stat_staff')
        self.customer_user, self.customer_profile = make_customer('stat_cust')

    def test_customer_cannot_access_statistics(self):
        self.client.force_login(self.customer_user)
        response = self.client.get(reverse('catalog:statistics'))
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse('catalog:statistics'))
        self.assertRedirects(response, reverse('login'))

    def test_staff_can_access_statistics(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('catalog:statistics'))
        self.assertEqual(response.status_code, 200)

    def test_statistics_shows_product_list(self):
        product = make_product('Mille-feuille')
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('catalog:statistics'))
        self.assertContains(response, 'Mille-feuille')

    def test_statistics_shows_metrics_with_no_data(self):
        """When there are no completed orders, metrics should show a no-data message."""
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('catalog:statistics'))
        self.assertContains(response, 'No completed orders to calculate sales statistics')

    def test_statistics_shows_sales_metrics(self):
        """With completed orders, mean/median/mode should appear on the page."""
        product = make_product('Croissant')
        order = Order.objects.create(
            client=self.customer_profile,
            payment_type=Order.PaymentType.CASH,
            status=Order.OrderStatus.COMPLETED,
            final_price='15.00',
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            purchase_price='15.00',
            historical_product_name=product.name,
        )
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('catalog:statistics'))
        self.assertContains(response, 'Mean')
        self.assertContains(response, 'Median')
        self.assertContains(response, 'Mode')

    def test_statistics_chart_images_rendered(self):
        """The page should contain inline base64 chart images."""
        make_product('Opera Cake')
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('catalog:statistics'))
        self.assertContains(response, 'data:image/png;base64,')

    def test_statistics_product_filter_for_chart(self):
        """Selecting a product via GET param selects it as chart subject."""
        product = make_product('Tarte Tatin')
        self.client.force_login(self.staff_user)
        response = self.client.get(
            reverse('catalog:statistics'),
            {'product_id': product.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tarte Tatin')


# ---------------------------------------------------------------------------
# Staff creation view tests
# ---------------------------------------------------------------------------

class StaffCreationViewTests(TestCase):
    """Tests for GET/POST /staff/create/ — Admin only."""

    def setUp(self):
        self.admin_user, self.admin_profile = make_admin('sc_admin')
        self.staff_user, self.staff_profile = make_staff('sc_staff')
        self.customer_user, _ = make_customer('sc_cust')

        # Valid payload that satisfies all constraints
        self.valid_payload = {
            'username': 'new_staff_member',
            'first_name': 'Alice',
            'last_name': 'Baker',
            'email': 'alice@pastry.example',
            'password': 'Str0ngP@ss!',
            'password_confirm': 'Str0ngP@ss!',
            'position': 'Head Chef',
            'date_of_birth': '1990-06-15',
            'contact_details': 'ext. 202',
        }

    # ---- Access control ----

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse('staff_create'))
        self.assertRedirects(response, reverse('login'))

    def test_customer_is_denied(self):
        self.client.force_login(self.customer_user)
        response = self.client.get(reverse('staff_create'))
        self.assertEqual(response.status_code, 403)

    def test_staff_role_is_denied(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('staff_create'))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_form(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('staff_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Staff Account')

    # ---- Successful creation ----

    def test_valid_post_creates_user_and_profile(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('staff_create'), self.valid_payload)
        self.assertRedirects(response, reverse('staff_list'))

        # User created with STAFF role
        user = User.objects.get(username='new_staff_member')
        self.assertEqual(user.role, User.Role.STAFF)
        self.assertEqual(user.first_name, 'Alice')
        self.assertTrue(user.check_password('Str0ngP@ss!'))

        # StaffProfile linked
        self.assertTrue(hasattr(user, 'staff_profile'))
        self.assertEqual(user.staff_profile.position, 'Head Chef')
        self.assertEqual(str(user.staff_profile.date_of_birth), '1990-06-15')

    def test_valid_post_shows_success_message(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse('staff_create'), self.valid_payload, follow=True
        )
        self.assertContains(response, 'created successfully')

    def test_underage_leaves_no_partial_user(self):
        """If date_of_birth fails validation, no partial User is created."""
        payload = dict(self.valid_payload)
        payload['username'] = 'partial_user'
        payload['date_of_birth'] = '2015-01-01'  # under 18

        self.client.force_login(self.admin_user)
        self.client.post(reverse('staff_create'), payload)

        self.assertFalse(User.objects.filter(username='partial_user').exists())

    # ---- Validation failures ----

    def test_duplicate_username_rejected(self):
        self.client.force_login(self.admin_user)
        payload = dict(self.valid_payload)
        payload['username'] = self.staff_user.username  # already exists

        response = self.client.post(reverse('staff_create'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')

    def test_password_mismatch_rejected(self):
        self.client.force_login(self.admin_user)
        payload = dict(self.valid_payload)
        payload['password_confirm'] = 'WrongPassword!'

        response = self.client.post(reverse('staff_create'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'do not match')

    def test_underage_date_of_birth_rejected(self):
        self.client.force_login(self.admin_user)
        payload = dict(self.valid_payload)
        payload['username'] = 'young_staff'
        payload['date_of_birth'] = '2015-01-01'  # under 18

        response = self.client.post(reverse('staff_create'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='young_staff').exists())

    def test_missing_required_field_rejected(self):
        self.client.force_login(self.admin_user)
        payload = dict(self.valid_payload)
        del payload['position']  # required StaffProfile field

        response = self.client.post(reverse('staff_create'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='new_staff_member').exists())

    def test_form_has_both_fieldsets(self):
        """The form page should contain both Account Details and Staff Profile fieldsets."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('staff_create'))
        self.assertContains(response, 'Account Details')
        self.assertContains(response, 'Staff Profile')
