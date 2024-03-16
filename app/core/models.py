from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

import uuid
import os

ORDER_STATUS = (
    ('PENDING', 'Pending'),
    ('CONFIRMED', 'Confirmed'),
    ('PREPARING', 'Preparing'),
    ('READY', 'Ready'),
    ('DELIVERED', 'Delivered'),
    ('CANCELLED', 'Cancelled'),
    ('NOT_PLACED', 'Not Placed'),
)

PAYMENT_METHOD = (
    ('CASH', 'Cash'),
    ('CARD', 'Card'),
)

FOOD_TYPE = (
    ('STARTER', 'Starter'),
    ('MAIN_COURSE', 'Main Course'),
    ('DESSERT', 'Dessert'),
    ('DRINK', 'Drink'),
)


def food_item_image_file_path(instance, filename):
    """Generate file path for new food item image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads', 'food_item', filename)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class FoodItem(models.Model):
    """FoodItem object."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    available = models.BooleanField(default=False)
    image = models.ImageField(null=True, upload_to=food_item_image_file_path)
    type = models.CharField(max_length=20, choices=FOOD_TYPE, default='MAIN_COURSE')

    def __str__(self):
        return self.name


class Address(models.Model):
    """Address object."""
    user = models.ForeignKey(
        User,
        related_name='addresses',
        on_delete=models.CASCADE,
    )
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    CEP = models.PositiveIntegerField()
    street = models.CharField(max_length=255)
    number = models.PositiveIntegerField()
    complement = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.street}, {self.number}"


class OrderFoodItem(models.Model):
    food_item = models.ForeignKey(
        FoodItem,
        related_name='order_items',
        on_delete=models.SET_NULL,
        null=True,
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.food_item} - {self.quantity}"


class Order(models.Model):
    """Order object."""
    user = models.ForeignKey(
        User,
        related_name='orders',
        on_delete=models.CASCADE,
    )
    order_items = models.ManyToManyField(OrderFoodItem, default=None, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='NOT_PLACED')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='CASH')
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    @property
    def total_price(self):
        """Calculate and return total price of order."""
        total = 0
        for order_item in self.order_items.all():
            total += order_item.food_item.price * order_item.quantity

        return total

    @property
    def total_items(self):
        """Calculate and return total number of items in order."""
        total = 0
        for order_item in self.order_items.all():
            total += order_item.quantity

        return total

    def __str__(self):
        return f'{self.user} - {self.date}'
