import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from market.filters import ProductFilter
from market.models import Product, ProductReview, ProductCharacteristics, Property, GroupProperties, \
    ProductAvailability
from market.serializers import ProductSerializer, ProductDetailSerializer, ProductReviewSerilalizer, \
    CharacteristicsSerializer, CharacteristicsBaseSerializer, PropertiesSerializer, GroupPropertiesSerializer, \
    PropertiesBaseSerializer, ProductCreateSerializer, ProductAvailabilitySerializer

import logging

logger = logging.getLogger(__name__)


class ProductList(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('name',)
    filter_class = ProductFilter

    def get_serializer_class(self):
        if self.action == 'list':
            logger.info('list of products')
            return ProductSerializer
        elif self.action == 'create':
            logger.info('create product')
            return ProductCreateSerializer
        return ProductDetailSerializer


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
    queryset = ProductCharacteristics.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            logger.info('list of characteristics')
            return CharacteristicsSerializer
        return CharacteristicsBaseSerializer


class ProductReviewView(viewsets.ViewSet):

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = (AllowAny,)
        else:
            permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def list(self, request, product_id):
        try:
            logger.info('list of product reviews')
            reviews = ProductReview.objects.get_reviews(product_id=product_id)
            serializer = ProductReviewSerilalizer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'list of product reviews - {str(e)}')
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, product_id):
        try:
            logger.info('list of product reviews')
            product = Product.objects.get(id=product_id)
            serializer = ProductReviewSerilalizer(data=request.data)
            if serializer.is_valid():
                review = serializer.save(user=request.user)
                product.reviews.add(review)
                return Response({'success': True}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f'list of product reviews - {str(e)}')
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductReviewDetailsView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, product_id, review_id):
        try:
            logger.info(f'delete review: {review_id}')
            review = ProductReview.objects.get(id=review_id)
            review.delete()
            return Response({'success': True})
        except ProductReview.DoesNotExist as e:
            logger.error(f'delete review: {review_id}')
            return Response({"error": e})


class DiscountView(viewsets.ViewSet):
    def post(self, request):
        try:
            logger.info('create discount')
            data = json.loads(request.body)
            Product.objects.set_discounts(data['product_ids'], data['discount'])
            return Response({'success': True})
        except Exception as e:
            logger.error(f'create discount - {str(e)}')
            return Response({'error': e})


class RemoveDiscountView(viewsets.ViewSet):
    def post(self, request):
        try:
            logger.info('remove discounts')
            data = json.loads(request.body)
            product_ids = data['product_ids']
            Product.objects.remove_discounts(product_ids)
            return Response({'success': True})
        except Exception as e:
            logger.error('remove discounts')
            return Response({'error': e})


class ProductAvailabilityView(viewsets.ModelViewSet):
    queryset = ProductAvailability.objects.all()
    serializer_class = ProductAvailabilitySerializer