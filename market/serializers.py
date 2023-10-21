from rest_framework import serializers

from auth_.serializers import UserSerializer
from core.serializers import BrandSerializer
from .models import ProductReview, ProductCharacteristics, Product, Property, GroupProperties, \
    ProductAvailability


class ProductReviewSerilalizer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'review', 'rating']


class GroupPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupProperties
        fields = '__all__'


class PropertiesBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'


class PropertiesSerializer(PropertiesBaseSerializer):
    group = GroupPropertiesSerializer()

    class Meta:
        model = Property
        fields = PropertiesBaseSerializer.Meta.fields


class CharacteristicsBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCharacteristics
        fields = '__all__'


class CharacteristicsSerializer(CharacteristicsBaseSerializer):
    property = serializers.CharField(source='property.name')

    class Meta:
        model = ProductCharacteristics
        fields = CharacteristicsBaseSerializer.Meta.fields


class ProductSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'real_price', 'current_price', 'discount', 'image', 'rating']


class ProductDetailSerializer(ProductSerializer):
    brand = BrandSerializer(read_only=True)
    characteristics = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['category', 'brand', 'characteristics', 'is_recommended',
                                                  'is_popular']

    def get_characteristics(self, obj):
        characteristics = obj.characteristics.filter(property__is_description=True)
        return CharacteristicsSerializer(characteristics, many=True).data


class ProductCreateSerializer(ProductSerializer):
    characteristics = serializers.ListSerializer(child=serializers.IntegerField(), write_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['category', 'brand', 'characteristics', 'is_recommended',
                                                  'is_popular']

    def create(self, validated_data):
        characteristics_ids = validated_data.pop('characteristics')
        product = Product.objects.create(**validated_data)
        characteristics = ProductCharacteristics.objects.filter(id__in=characteristics_ids)
        for ch in characteristics:
            product.characteristics.add(ch.id)
        return product


class ProductAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAvailability
        fields = ['id', 'product', 'shop', 'amount']