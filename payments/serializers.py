import datetime

from rest_framework import serializers

from payments.models import CreditCard, Order, Transaction, Favorite, FavoriteItem
from market.serializers import ApartmentSerializer
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


class favoriteSerializer(serializers.ModelSerializer):
    favorite_items = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ['user', 'favorite_items', 'total_sum']

    def get_favorite_items(self, obj):
        print(obj.favorite_items.all())
        return FavoriteItemSerializer(obj.favorite_items.all(), many=True).data


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['favorite', 'availability']


class TransactionReadSerializer(serializers.ModelSerializer):
    favorite = favoriteSerializer()

    class Meta:
        model = Transaction
        fields = ['favorite', 'date_created']


class OrderSerializer(serializers.ModelSerializer):
    transaction = TransactionReadSerializer()

    class Meta:
        model = Order
        fields = ['id', 'transaction', 'status', 'assignee']


class FavoriteItemSerializer(serializers.ModelSerializer):
    Apartment = ApartmentSerializer()

    class Meta:
        model = FavoriteItem
        fields = '__all__'