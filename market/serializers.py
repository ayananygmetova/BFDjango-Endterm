from rest_framework import serializers

from auth_.serializers import UserSerializer
from core.serializers import BrandSerializer
from .models import ApartmentReview, ApartmentCharacteristics, Apartment, Property, GroupProperties, \
    ApartmentAvailability


class ApartmentReviewSerilalizer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ApartmentReview
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
        model = ApartmentCharacteristics
        fields = '__all__'


class CharacteristicsSerializer(CharacteristicsBaseSerializer):
    property = serializers.CharField(source='property.name')

    class Meta:
        model = ApartmentCharacteristics
        fields = CharacteristicsBaseSerializer.Meta.fields


class ApartmentSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Apartment
        fields = ['id', 'name', 'real_price', 'current_price', 'discount', 'image', 'rating']


class ApartmentDetailSerializer(ApartmentSerializer):
    brand = BrandSerializer(read_only=True)
    characteristics = serializers.SerializerMethodField()

    class Meta(ApartmentSerializer.Meta):
        fields = ApartmentSerializer.Meta.fields + ['category', 'brand', 'characteristics', 'is_recommended',
                                                  'is_popular']

    def get_characteristics(self, obj):
        characteristics = obj.characteristics.filter(property__is_description=True)
        return CharacteristicsSerializer(characteristics, many=True).data


class ApartmentCreateSerializer(ApartmentSerializer):
    characteristics = serializers.ListSerializer(child=serializers.IntegerField(), write_only=True)

    class Meta(ApartmentSerializer.Meta):
        fields = ApartmentSerializer.Meta.fields + ['category', 'brand', 'characteristics', 'is_recommended',
                                                  'is_popular']

    def create(self, validated_data):
        characteristics_ids = validated_data.pop('characteristics')
        Apartment = Apartment.objects.create(**validated_data)
        characteristics = ApartmentCharacteristics.objects.filter(id__in=characteristics_ids)
        for ch in characteristics:
            Apartment.characteristics.add(ch.id)
        return Apartment


class ApartmentAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentAvailability
        fields = ['id', 'Apartment', 'shop', 'amount']