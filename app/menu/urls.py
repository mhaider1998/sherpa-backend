from django.urls import path, include
from menu import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('food-item', views.FoodItemViewSet)
router.register('orders', views.OrderViewSet)
router.register('order-items', views.OrderFoodItemViewSet)

app_name = 'menu'

urlpatterns = [
    path('', include(router.urls))
]
