"""
Tests for the menu API.
"""

from decimal import Decimal
from unittest import TestCase

from core import models
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from menu.serializers import (
    FoodItemSerializer,
    FoodItemDetailSerializer,
)

FOOD_ITEM_URL = reverse('menu:fooditem-list')


def detail_url(food_item_id):
    return reverse('menu:fooditem-detail', args=[food_item_id])


def create_food_item(**params):
    """Create and return a sample food item"""
    defaults = {
        'name': 'Food name',
        'description': 'Food description',
        'price': Decimal('10.50'),
        'available': True,
    }
    # If params are provided overwrite defaults
    defaults.update(**params)

    food_item = models.FoodItem.objects.create(**defaults)
    return food_item


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicFoodItemAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_food_item(self):
        """Test retrieving a list of food items"""
        create_food_item()
        create_food_item()

        res = self.client.get(FOOD_ITEM_URL)

        food_items = models.FoodItem.objects.all()
        serializer = FoodItemSerializer(food_items, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_food_item_detail(self):
        food_item = create_food_item()

        url = detail_url(food_item.id)
        res = self.client.get(url)

        serializer = FoodItemDetailSerializer(food_item)
        self.assertEqual(res.data, serializer.data)


class PrivateFoodItemAPITest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        try:
            self.user = models.User.objects.get(email='user@example.com')
        except models.User.DoesNotExist:
            # If the user doesn't exist, create it
            self.user = create_user(
                email='user@example.com', password='testpass123'
            )
        self.client.force_authenticate(self.user)

    def test_create_food_item(self):
        payload = {
            'name': 'Test name',
            'price': Decimal('10.50'),
            'available': True
        }
        res = self.client.post(FOOD_ITEM_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        food_item = models.FoodItem.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(food_item, k), v)

    def test_partial_update(self):
        original_price = Decimal('9.99')
        food_item = create_food_item(
            name='Food name',
            description='Food description',
            price=Decimal(original_price),
            available=True,
        )

        payload = {'name': 'New food name'}
        url = detail_url(food_item.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        food_item.refresh_from_db()
        self.assertEqual(food_item.name, payload['name'])
        self.assertEqual(food_item.price, original_price)

    def test_full_update(self):
        food_item = create_food_item()
        payload = {
            'name': 'New food name',
            'description': 'New food description',
            'price': Decimal('20.00'),
            'available': False,
        }
        url = detail_url(food_item.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        food_item.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(food_item, k), v)

    def test_delete_food_item(self):
        food_item = create_food_item()
        url = detail_url(food_item.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.FoodItem.objects.filter(id=food_item.id).exists())
