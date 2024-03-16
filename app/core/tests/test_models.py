from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        '''
        Test creating a new user with an email is successful.
        '''
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.check_password(password), True)

    def test_new_user_email_normalized(self):
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'pass123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'pass123')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            'test123@example.com',
            'pass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_item(self):
        """Test creating a item is successful."""
        food_item = models.FoodItem.objects.create(
            name='Food name',
            description='Food description',
            price=Decimal('14.50'),
            available=True,
            image='/food.jpg',
        )

        self.assertEqual(str(food_item), food_item.name)

    def test_create_order(self):
        """Test creating a order is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            name='Test user',
            password=password,
        )

        food_item_1 = models.FoodItem.objects.create(
            name='Food name',
            description='Food description',
            price=Decimal('30'),
            available=True,
        )

        food_item_2 = models.FoodItem.objects.create(
            name='Food name',
            description='Food description',
            price=Decimal('14.50'),
            available=True,
        )

        order_item = models.OrderFoodItem.objects.create(
            food_item=food_item_1,
            quantity=2,
        )

        order_item_2 = models.OrderFoodItem.objects.create(
            food_item=food_item_2,
            quantity=1,
        )

        order = models.Order.objects.create(
            user=user,
        )

        order.order_items.add(order_item)
        order.order_items.add(order_item_2)

        self.assertEqual(order.user, user)
        self.assertEqual(order.total_items, 3)
        self.assertEqual(order.total_price, Decimal('74.50'))
        self.assertEqual(str(order), f"{order.user} - {order.date}")
