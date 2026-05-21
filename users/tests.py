from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRoleConstraintsTests(TestCase):
    def test_superuser_is_always_admin_and_staff(self):
        # Create a superuser and check if the role is automatically coerced to ADMIN and is_staff to True
        user = User.objects.create_superuser(
            username="super_admin", 
            email="super@example.com", 
            password="password123"
        )
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

        # Update a user's is_superuser flag to True and verify it is rejected for non-admin role
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
        self.assertTrue(user2.is_staff)  # STAFF must retain is_staff=True

    def test_admin_is_not_always_superuser(self):
        # Create an ADMIN who is NOT a superuser
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
        # Create a STAFF user and assert that is_superuser is False but is_staff is True
        staff_user = User.objects.create_user(
            username="just_staff",
            email="staff2@example.com",
            password="password123",
            role=User.Role.STAFF
        )
        self.assertEqual(staff_user.role, User.Role.STAFF)
        self.assertFalse(staff_user.is_superuser)
        self.assertTrue(staff_user.is_staff)  # STAFF must have is_staff=True

        # Try to save a STAFF user as is_superuser and check if save overrides it
        staff_user.is_superuser = True
        staff_user.save()
        self.assertFalse(staff_user.is_superuser)
        self.assertTrue(staff_user.is_staff)  # is_staff must remain True

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

        # Try to save a CUSTOMER user with is_superuser=True or is_staff=True
        customer.is_superuser = True
        customer.is_staff = True
        customer.save()
        self.assertFalse(customer.is_superuser)
        self.assertFalse(customer.is_staff)

    def test_clean_validation_errors(self):
        # Test clean() validation for invalid combinations
        user = User(username="invalid_user", role=User.Role.STAFF, is_superuser=True)
        with self.assertRaises(ValidationError):
            user.clean()

        user2 = User(username="invalid_user2", role=User.Role.CUSTOMER, is_superuser=True)
        with self.assertRaises(ValidationError):
            user2.clean()
