import datetime

from rest_framework import serializers

from payments.models import CreditCard, Order, Transaction, Cart, CartItem
from market.serializers import ProductSerializer
from common import messages


class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = ['balance', 'user']

    def validate_balance(self, value):
        if value < 0:
            raise Exception(messages.NO_MONEY)
        return value

    def create(self, validated_data):
        valid_thru = (datetime.datetime.now() + datetime.timedelta(weeks=156)).date()
        validated_data['valid_thru'] = valid_thru
        card = CreditCard.objects.create(**validated_data)
        return card


class CartSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['user', 'cart_items', 'total_sum']

    def get_cart_items(self, obj):
        return CartItemSerializer(obj.cart_items.all(), many=True).data


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['cart', ]


class TransactionReadSerializer(serializers.ModelSerializer):
    cart = CartSerializer()

    class Meta:
        model = Transaction
        fields = ['cart', 'date_created']


class OrderSerializer(serializers.ModelSerializer):
    transaction = TransactionReadSerializer()

    class Meta:
        model = Order
        fields = ['id', 'transaction', 'status', 'assignee']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = '__all__'