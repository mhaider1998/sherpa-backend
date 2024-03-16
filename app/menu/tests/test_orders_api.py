"""
Tests for the orders API.
"""

from django.test import TestCase
from decimal import Decimal

from core import models
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

from menu.serializers import (
    OrderSerializer,
)

ORDERS_URL = reverse('menu:order-list')
ORDERS_HISTORY_URL = reverse('menu:order-history')


def detail_url(order_id):
    return reverse('menu:order-detail', args=[order_id])


def order_item_url(order_item_id):
    return reverse('menu:orderfooditem-detail', args=[order_item_id])


def create_user(email='user@example.com', password='pass123'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicOrdersApiTest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateOrdersApiTest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_orders(self):
        """Test retrieving order not placed (in cart)"""
        models.Order.objects.create(user=self.user)
        models.Order.objects.create(user=self.user, status='READY')

        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['status'], 'NOT_PLACED')

    def test_orders_limited_to_user(self):
        """Test list if orders is limited to authenticated user."""
        pass
        user2 = create_user(email='user2@example.com')
        models.Order.objects.create(user=user2)
        order = models.Order.objects.create(user=self.user)

        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], order.id)

    def test_update_order(self):
        order = models.Order.objects.create(user=self.user)

        payload = {'status': 'READY'}
        url = detail_url(order.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, payload['status'])

    def test_delete_order(self):
        order = models.Order.objects.create(user=self.user)

        url = detail_url(order.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        orders = models.Order.objects.filter(user=self.user)
        self.assertFalse(orders.exists())

    def test_create_order_with_existing_food_item(self):
        """Test creating order with existing food items."""
        food_item = models.FoodItem.objects.create(name='Soup', price=Decimal('10.00'))
        food_item2 = models.FoodItem.objects.create(name='Salad', price=Decimal('14.00'))

        payload = {
            "order_items": [{"food_item": food_item.id, "quantity": 1},
                            {"food_item": food_item2.id, "quantity": 1}],
            }

        res = self.client.post(ORDERS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        orders = models.Order.objects.filter(user=self.user)
        self.assertEqual(orders.count(), 1)
        order = orders[0]
        self.assertEqual(order.status, 'NOT_PLACED')
        self.assertEqual(order.order_items.count(), 2)
        for item in payload['order_items']:
            exists = order.order_items.filter(
                food_item__id=item['food_item'],
            ).exists()
            self.assertTrue(exists)

    def test_can_only_create_order_with_existing_food_item(self):
        """Test that order can only be created with existing food items."""
        payload = {
            "order_items": [{"food_item": 99, "quantity": 1}]
            }

        res = self.client.post(ORDERS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_order_history(self):
        """Test retrieving order history."""
        models.Order.objects.create(user=self.user, status='READY')
        models.Order.objects.create(user=self.user)

        res = self.client.get(ORDERS_HISTORY_URL)

        orders = models.Order.objects.all().order_by('-id')
        serializer = OrderSerializer(orders, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_order_detail(self):
        """Test if orders food items details are retrieved."""
        order = models.Order.objects.create(user=self.user)

        food_item = models.FoodItem.objects.create(
            name='Food name',
            description='Food description',
            price=Decimal('30.00'),
            available=True,
        )

        order_item = models.OrderFoodItem.objects.create(
            food_item=food_item,
            quantity=1,
        )

        order.order_items.add(order_item)

        url = detail_url(order.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res_order_detail = res.data["order_items"][0]

        self.assertEqual(res_order_detail['food_item']['id'], food_item.id)
        self.assertEqual(res_order_detail['food_item']['name'], food_item.name)
        self.assertEqual(res_order_detail['food_item']['description'], food_item.description)
        self.assertEqual(res_order_detail['food_item']['price'], str(food_item.price))
        self.assertEqual(res_order_detail['food_item']['available'], food_item.available)

    def test_update_order_item(self):
        """Test updating an order item."""
        order_item = models.OrderFoodItem.objects.create(
            food_item=models.FoodItem.objects.create(name='Food name', price=Decimal('30.00')),
            quantity=1,
        )
        payload = {'quantity': 2}

        url = order_item_url(order_item.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        order_item.refresh_from_db()
        self.assertEqual(order_item.quantity, payload['quantity'])

    def test_delete_order_item(self):
        '''Test deleting a order item'''
        order_item = models.OrderFoodItem.objects.create(
            food_item=models.FoodItem.objects.create(name='Food name', price=Decimal('30.00')),
            quantity=1,
        )
        url = order_item_url(order_item.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.OrderFoodItem.objects.filter(id=order_item.id).exists())
