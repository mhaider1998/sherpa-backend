from rest_framework import viewsets, permissions, authentication, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import (
    FoodItem,
    Order,
    OrderFoodItem,
    )
from menu import (
    serializers,

)


class AuthenticatedForWriteMethods(permissions.BasePermission):
    """
    Custom permisson class to require authentication for write methods.
    """

    def has_permission(self, request, view):
        # Safe methods: GET and HEAD.
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated


class FoodItemViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FoodItemDetailSerializer
    queryset = FoodItem.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [AuthenticatedForWriteMethods]

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.FoodItemSerializer

        return self.serializer_class


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.OrderDetailSerializer
    queryset = Order.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer class when POST request is made."""
        if self.action == 'create':
            return serializers.OrderSerializer

        return self.serializer_class

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user, status="NOT_PLACED").order_by('-id')

    @action(detail=False, methods=['GET'])
    def history(self, request):
        """Return orders history."""
        orders = self.queryset.filter(user=request.user).order_by('-id')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


class OrderFoodItemViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.OrderFoodItemSerializer
    queryset = OrderFoodItem.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
