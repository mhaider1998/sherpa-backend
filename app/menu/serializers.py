from rest_framework import serializers

from core.models import (
    FoodItem,
    Order,
    OrderFoodItem,
    )


class FoodItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'description', 'price', 'available', 'image', 'type']
        read_only_fields = ['id']


class FoodItemDetailSerializer(FoodItemSerializer):

    class Meta(FoodItemSerializer.Meta):
        fields = FoodItemSerializer.Meta.fields


class OrderFoodItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderFoodItem
        fields = ['id', 'food_item', 'quantity']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderFoodItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'order_items', 'status', 'payment_method', 'total_price', 'total_items', 'delivery_address']
        read_only_fields = ['id']

    def create(self, validated_data):
        # query if the an order with status 'NOT_PLACED' exists for the user
        auth_user = self.context['request'].user
        order = Order.objects.filter(
            user=auth_user,
            status='NOT_PLACED'
        ).first()
        # if order exists, add food items to the order
        if order:
            order_items = validated_data.pop('order_items', [])
            for item in order_items:
                quantity = item.pop('quantity', 1)
                try:
                    food_obj = FoodItem.objects.get(id=item['food_item'].id)
                    item_obj = OrderFoodItem.objects.create(
                        food_item=food_obj,
                        quantity=quantity
                    )
                    order.order_items.add(item_obj)
                except FoodItem.DoesNotExist:
                    raise serializers.ValidationError(
                        'Food item does not exist.'
                    )
        else:
            # else create a new order
            order_items = validated_data.pop('order_items', [])
            auth_user = self.context['request'].user
            order = Order.objects.create(user=auth_user)

            for item in order_items:
                quantity = item.pop('quantity', 1)
                try:
                    food_obj = FoodItem.objects.get(id=item['food_item'].id)
                    item_obj = OrderFoodItem.objects.create(
                        food_item=food_obj,
                        quantity=quantity
                    )
                    order.order_items.add(item_obj)
                except FoodItem.DoesNotExist:
                    raise serializers.ValidationError(
                        'Food item does not exist.'
                    )

        return order


class OrderFoodItemDetailSerializer(OrderFoodItemSerializer):
    food_item = FoodItemSerializer()

    class Meta(OrderFoodItemSerializer.Meta):
        fields = OrderFoodItemSerializer.Meta.fields
        read_only_fields = ['id']


class OrderDetailSerializer(OrderSerializer):
    order_items = OrderFoodItemDetailSerializer(many=True, required=False)

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields
        read_only_fields = ['id']
