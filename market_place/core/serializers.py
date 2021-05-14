from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from common import messages
from .models import Category, Brand, Shop, City


class CitySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()

    def create(self, validated_data):
        city = City.objects.create(**validated_data)
        return city

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    parent_id = serializers.IntegerField(allow_null=True)

    def validate_name(self, value):
        special_characters = "!#$%^&*()-+?_=,<>/"
        if any(val in special_characters for val in value):
            raise Exception(messages.SPECIAL_CHARACTERS)
        return value

    def create(self, validated_data):
        category = Category.objects.create(**validated_data)
        return category

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.parent_id = validated_data.get('parent_id', instance.parent_id)
        instance.save()
        return instance


class CategoryListSerializer(serializers.ModelSerializer):
    children = serializers.ListSerializer(read_only=True, child=RecursiveField())

    class Meta:
        model = Category
        fields = ['id', 'name', 'children']


class BrandSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    detail = serializers.CharField(allow_null=True)
    image = serializers.ImageField()

    def validate_name(self, value):
        special_characters = "!#$%^&*()-+?_=,<>/"
        if any(val in special_characters for val in value):
            raise Exception(messages.SPECIAL_CHARACTERS)
        return value

    def create(self, validated_data):
        brand = Brand.objects.create(**validated_data)
        return brand

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.detail = validated_data.get('detail', instance.detail)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'