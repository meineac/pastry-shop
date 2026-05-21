from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
import decimal

from users.models import User, CustomerProfile
from catalog.models import Product, Category, Manufacturer
from purchasing.models import Cart, CartItem, Order, OrderItem, PickupPoint, PromoCode

class PurchasingTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create categories
        self.cat1 = Category.objects.create(name="Cakes")
        self.cat2 = Category.objects.create(name="Cookies")
        
        # Create manufacturers
        self.man1 = Manufacturer.objects.create(name="Sweet Bakers")
        self.man2 = Manufacturer.objects.create(name="Cookie Factory")
        
        # Create products
        self.prod1 = Product.objects.create(
            name="Chocolate Cake",
            category=self.cat1,
            manufacturer=self.man1,
            price=decimal.Decimal("25.00"),
            unit_of_measurement=Product.UnitMeasurement.PIECES,
            quantity=10,
            ingredients="Chocolate, flour, sugar",
            is_active=True
        )
        self.prod2 = Product.objects.create(
            name="Vanilla Cookie",
            category=self.cat2,
            manufacturer=self.man2,
            price=decimal.Decimal("1.50"),
            unit_of_measurement=Product.UnitMeasurement.KILOGRAMS,
            quantity=50,
            ingredients="Vanilla, flour, butter",
            is_active=True
        )
        self.prod_inactive = Product.objects.create(
            name="Old Pastry",
            category=self.cat1,
            manufacturer=self.man1,
            price=decimal.Decimal("10.00"),
            unit_of_measurement=Product.UnitMeasurement.PIECES,
            quantity=5,
            ingredients="Expired ingredients",
            is_active=False
        )

        # Create customer user
        self.user = User.objects.create_user(username="customer", password="password123", role=User.Role.CUSTOMER)
        self.profile = CustomerProfile.objects.create(
            user=self.user,
            date_of_birth=date(1995, 5, 15),
            phone_number="+375 (29) 111-22-33"
        )
        
        # Create Pickup Point
        self.pickup_point = PickupPoint.objects.create(
            address="123 Main St",
            working_hours="9:00 - 21:00",
            price=decimal.Decimal("1.00")
        )
        
        # Create Promo Codes
        self.promo_valid = PromoCode.objects.create(
            code="SAVE20",
            expiration_date=date.today() + timedelta(days=5),
            status=PromoCode.Status.ACTIVE,
            discount_percentage=decimal.Decimal('20.00'),
            minimum_purchase_amount=decimal.Decimal('10.00'),
            conditions_of_application="20% off on orders over $10.00",
            is_hidden=False
        )
        self.promo_expired = PromoCode.objects.create(
            code="SAVE50",
            expiration_date=date.today() - timedelta(days=5),
            status=PromoCode.Status.ACTIVE,
            discount_percentage=decimal.Decimal('50.00'),
            minimum_purchase_amount=decimal.Decimal('0.00'),
            conditions_of_application="50% off — expired.",
            is_hidden=False
        )
        self.promo_high_min = PromoCode.objects.create(
            code="MIN100",
            expiration_date=date.today() + timedelta(days=5),
            status=PromoCode.Status.ACTIVE,
            discount_percentage=decimal.Decimal('15.00'),
            minimum_purchase_amount=decimal.Decimal('100.00'),
            conditions_of_application="15% discount on purchases over $100.00",
            is_hidden=False
        )

    def test_catalog_filtering_and_searching(self):
        # Test basic search query
        response = self.client.get(reverse('catalog:product_list'), {'q': 'Chocolate'})
        self.assertContains(response, "Chocolate Cake")
        self.assertNotContains(response, "Vanilla Cookie")

        # Test search query by category name
        response = self.client.get(reverse('catalog:product_list'), {'q': 'Cookies'})
        self.assertContains(response, "Vanilla Cookie")
        self.assertNotContains(response, "Chocolate Cake")

        # Test filter by category
        response = self.client.get(reverse('catalog:product_list'), {'category': self.cat1.id})
        self.assertContains(response, "Chocolate Cake")
        self.assertNotContains(response, "Vanilla Cookie")

        # Test filter by manufacturer
        response = self.client.get(reverse('catalog:product_list'), {'manufacturer': self.man2.id})
        self.assertContains(response, "Vanilla Cookie")
        self.assertNotContains(response, "Chocolate Cake")

        # Test filter by price range
        response = self.client.get(reverse('catalog:product_list'), {'min_price': '10.00', 'max_price': '30.00'})
        self.assertContains(response, "Chocolate Cake")
        self.assertNotContains(response, "Vanilla Cookie")

    def test_add_to_cart_guest_redirects_to_registration(self):
        response = self.client.post(reverse('purchasing:add_to_cart', args=[self.prod1.id]))
        self.assertRedirects(response, reverse('register'))

    def test_cart_operations_authenticated(self):
        self.client.login(username="customer", password="password123")
        
        # Add to cart
        response = self.client.post(reverse('purchasing:add_to_cart', args=[self.prod1.id]))
        # Should redirect to cart page
        self.assertRedirects(response, reverse('purchasing:cart'))
        
        # Verify cart item was created
        cart = Cart.objects.get(client=self.profile)
        self.assertEqual(cart.items.count(), 1)
        item = cart.items.first()
        self.assertEqual(item.product, self.prod1)
        self.assertEqual(item.quantity, 1)
        
        # Add same item again to increment quantity
        self.client.post(reverse('purchasing:add_to_cart', args=[self.prod1.id]))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)
        
        # View cart
        response = self.client.get(reverse('purchasing:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chocolate Cake")
        self.assertContains(response, "2") # Quantity
        
        # Remove from cart
        response = self.client.post(reverse('purchasing:remove_from_cart', args=[item.id]))
        self.assertRedirects(response, reverse('purchasing:cart'))
        self.assertEqual(cart.items.count(), 0)

    def test_promo_code_validation(self):
        self.client.login(username="customer", password="password123")
        
        # Setup cart with Chocolate Cake ($25.00)
        self.client.post(reverse('purchasing:add_to_cart', args=[self.prod1.id]))
        
        # Apply valid promo code "SAVE20" (20% off)
        response = self.client.post(reverse('purchasing:checkout'), {
            'promo_code': 'SAVE20',
            'delivery_type': 'PICKUP',
            'payment_type': 'CASH'
        })
        self.assertEqual(response.status_code, 200)
        # 25 * 0.20 = 5.00 discount. Subtotal 25.00, discount 5.00
        self.assertContains(response, "Promo code applied successfully.")
        self.assertContains(response, "-$5.00")
        
        # Apply expired promo code
        response = self.client.post(reverse('purchasing:checkout'), {
            'promo_code': 'SAVE50',
            'delivery_type': 'PICKUP',
            'payment_type': 'CASH'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Promo code is expired.")
        
        # Apply invalid promo code
        response = self.client.post(reverse('purchasing:checkout'), {
            'promo_code': 'INVALID123',
            'delivery_type': 'PICKUP',
            'payment_type': 'CASH'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid promo code.")

        # Apply promo code with high minimum purchase requirements (MIN100)
        # Subtotal is $25.00, which is < $100.00
        response = self.client.post(reverse('purchasing:checkout'), {
            'promo_code': 'MIN100',
            'delivery_type': 'PICKUP',
            'payment_type': 'CASH'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "minimum purchase of $100.00")

    def test_checkout_delivery_pricing(self):
        self.client.login(username="customer", password="password123")
        self.client.post(reverse('purchasing:add_to_cart', args=[self.prod1.id]))
        
        # Test Pickup delivery option
        response = self.client.post(reverse('purchasing:checkout'), {
            'delivery_type': 'PICKUP',
            'pickup_point': self.pickup_point.id,
            'payment_type': 'CASH'
        })
        self.assertEqual(response.status_code, 200)
        # Subtotal: $25.00, Pickup Fee: $1.00 -> Total: $26.00
        self.assertContains(response, "Delivery Fee: $1.00")
        self.assertContains(response, "Total Price: $26.00")
        
        # Test Courier delivery option
        response = self.client.post(reverse('purchasing:checkout'), {
            'delivery_type': 'COURIER',
            'delivery_address': '123 Fake St',
            'payment_type': 'CARD'
        })
        self.assertEqual(response.status_code, 200)
        # Subtotal: $25.00, Courier Fee: $5.00 -> Total: $30.00
        self.assertContains(response, "Delivery Fee: $5.00")
        self.assertContains(response, "Total Price: $30.00")

    def test_place_order_and_stock_deduction(self):
        self.client.login(username="customer", password="password123")
        
        # Add prod1 (Chocolate Cake, 10 in stock, price $25)
        self.client.post(reverse('purchasing:add_to_cart', args=[self.prod1.id]))
        # Add prod2 (Vanilla Cookie, 50 in stock, price $1.50)
        self.client.post(reverse('purchasing:add_to_cart', args=[self.prod2.id]))
        
        # Apply promo SAVE20 (20% off)
        self.client.post(reverse('purchasing:checkout'), {
            'promo_code': 'SAVE20',
            'delivery_type': 'COURIER',
            'delivery_address': '456 Oak Ave',
            'payment_type': 'CARD'
        })
        
        # Place order
        response = self.client.post(reverse('purchasing:place_order'), {
            'delivery_type': 'COURIER',
            'delivery_address': '456 Oak Ave',
            'payment_type': 'CARD'
        })
        self.assertRedirects(response, reverse('profile'))
        
        # Verify Order and OrderItems are created
        order = Order.objects.latest('created_at')
        self.assertEqual(order.client, self.profile)
        self.assertEqual(order.delivery_type, Order.DeliveryType.COURIER)
        self.assertEqual(order.delivery_address, '456 Oak Ave')
        self.assertEqual(order.delivery_price, decimal.Decimal('5.00'))
        self.assertEqual(order.payment_type, Order.PaymentType.CARD)
        self.assertEqual(order.status, Order.OrderStatus.PENDING)
        self.assertEqual(order.promo_code, self.promo_valid)
        
        # Price: Subtotal = 26.50
        # Discount = 26.50 * 0.2 = 5.30
        # Delivery = 5.00
        # Final price = 26.50 - 5.30 + 5.00 = 26.20
        self.assertEqual(order.final_price, decimal.Decimal('26.20'))
        
        # Verify order items
        self.assertEqual(order.items.count(), 2)
        item1 = order.items.get(product=self.prod1)
        self.assertEqual(item1.quantity, 1)
        self.assertEqual(item1.purchase_price, decimal.Decimal('25.00'))
        self.assertEqual(item1.historical_product_name, "Chocolate Cake")
        
        # Verify stock quantities are decremented
        self.prod1.refresh_from_db()
        self.prod2.refresh_from_db()
        self.assertEqual(self.prod1.quantity, 9)
        self.assertEqual(self.prod2.quantity, 49)
        
        # Verify cart is cleared
        cart = Cart.objects.get(client=self.profile)
        self.assertEqual(cart.items.count(), 0)

    def test_checkout_auto_purges_inactive_items(self):
        self.client.login(username="customer", password="password123")
        
        # Add an active product
        self.client.post(reverse('purchasing:add_to_cart', args=[self.prod1.id]))
        # Manually create a cart item with the inactive product (add_to_cart_view blocks inactive items via POST)
        cart = Cart.objects.get(client=self.profile)
        CartItem.objects.create(cart=cart, product=self.prod_inactive, quantity=1)

        # Confirm there are 2 items in the cart before checkout
        self.assertEqual(cart.items.count(), 2)

        # GET checkout page - it should purge the inactive product and redirect to the cart page
        response = self.client.get(reverse('purchasing:checkout'))
        self.assertRedirects(response, reverse('purchasing:cart'))
        
        # Check if the inactive item was purged
        self.assertEqual(cart.items.count(), 1)
        self.assertFalse(cart.items.filter(product=self.prod_inactive).exists())

    def test_place_order_blocks_and_purges_inactive_items(self):
        self.client.login(username="customer", password="password123")
        
        # Setup cart with both active and inactive products
        self.client.post(reverse('purchasing:add_to_cart', args=[self.prod1.id]))
        cart = Cart.objects.get(client=self.profile)
        CartItem.objects.create(cart=cart, product=self.prod_inactive, quantity=1)

        self.assertEqual(cart.items.count(), 2)

        # POST to place_order_view
        response = self.client.post(reverse('purchasing:place_order'), {
            'delivery_type': 'COURIER',
            'delivery_address': '456 Oak Ave',
            'payment_type': 'CARD'
        })
        # Should redirect back to cart page
        self.assertRedirects(response, reverse('purchasing:cart'))

        # Inactive product must be purged
        self.assertEqual(cart.items.count(), 1)
        self.assertFalse(cart.items.filter(product=self.prod_inactive).exists())

        # No new orders should be created
        self.assertEqual(Order.objects.filter(client=self.profile).count(), 0)

