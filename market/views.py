import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from market.filters import ApartmentFilter
from market.models import Apartment, ApartmentReview, ApartmentCharacteristics, Property, GroupProperties, \
    ApartmentAvailability
from market.serializers import ApartmentSerializer, ApartmentDetailSerializer, ApartmentReviewSerilalizer, \
    CharacteristicsSerializer, CharacteristicsBaseSerializer, PropertiesSerializer, GroupPropertiesSerializer, \
    PropertiesBaseSerializer, ApartmentCreateSerializer, ApartmentAvailabilitySerializer

import logging

logger = logging.getLogger(__name__)


class ApartmentList(viewsets.ModelViewSet):
    queryset = Apartment.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('name',)
    filter_class = ApartmentFilter

    def get_serializer_class(self):
        if self.action == 'list':
            logger.info('list of Apartments')
            return ApartmentSerializer
        elif self.action == 'create':
            logger.info('create Apartment')
            return ApartmentCreateSerializer
        return ApartmentDetailSerializer


class GroupPropertiesView(viewsets.ModelViewSet):
    queryset = GroupProperties.objects.all()
    serializer_class = GroupPropertiesSerializer


class PropertiesView(viewsets.ModelViewSet):
    queryset = Property.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            logger.info('list of properties')
            return PropertiesSerializer
        return PropertiesBaseSerializer


class CharacteristicsView(viewsets.ModelViewSet):
    queryset = ApartmentCharacteristics.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            logger.info('list of characteristics')
            return CharacteristicsSerializer
        return CharacteristicsBaseSerializer


class ApartmentReviewView(viewsets.ViewSet):

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = (AllowAny,)
        else:
            permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def list(self, request, Apartment_id):
        try:
            logger.info('list of Apartment reviews')
            reviews = ApartmentReview.objects.get_reviews(Apartment_id=Apartment_id)
            serializer = ApartmentReviewSerilalizer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'list of Apartment reviews - {str(e)}')
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, Apartment_id):
        try:
            logger.info('list of Apartment reviews')
            Apartment = Apartment.objects.get(id=Apartment_id)
            serializer = ApartmentReviewSerilalizer(data=request.data)
            if serializer.is_valid():
                review = serializer.save(user=request.user)
                Apartment.reviews.add(review)
                return Response({'success': True}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f'list of Apartment reviews - {str(e)}')
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApartmentReviewDetailsView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, Apartment_id, review_id):
        try:
            logger.info(f'delete review: {review_id}')
            review = ApartmentReview.objects.get(id=review_id)
            review.delete()
            return Response({'success': True})
        except ApartmentReview.DoesNotExist as e:
            logger.error(f'delete review: {review_id}')
            return Response({"error": str(e)})


class DiscountView(viewsets.ViewSet):
    def post(self, request):
        try:
            logger.info('create discount')
            data = json.loads(request.body)
            Apartment.objects.set_discounts(data['Apartment_ids'], data['discount'])
            return Response({'success': True})
        except Exception as e:
            logger.error(f'create discount - {str(e)}')
            return Response({'error': e})


class RemoveDiscountView(viewsets.ViewSet):
    def post(self, request):
        try:
            logger.info('remove discounts')
            data = json.loads(request.body)
            Apartment_ids = data['Apartment_ids']
            Apartment.objects.remove_discounts(Apartment_ids)
            return Response({'success': True})
        except Exception as e:
            logger.error('remove discounts')
            return Response({'error': e})


class ApartmentAvailabilityView(viewsets.ModelViewSet):
    queryset = ApartmentAvailability.objects.all()
    serializer_class = ApartmentAvailabilitySerializer