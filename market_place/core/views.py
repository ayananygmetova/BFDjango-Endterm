from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.filters import BrandFilter
from core.models import Category, Brand, City, Shop
from core.serializers import CategorySerializer, CategoryListSerializer, BrandSerializer, CitySerializer, ShopSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        logger.info('category list')
        categories = Category.objects.filter(parent__isnull=True)
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        logger.info('category create')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'category create - {str(serializer.errors)}')
        return Response({'error': serializer.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist as e:
        logger.error({str(e)})
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = CategoryListSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        logger.info(f'change data of category')
        serializer = CategorySerializer(instance=category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f'change data of category {serializer.errors}')
        return Response({'error': serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'DELETE':
        category.delete()
        return Response({'info': 'deleted'})


class BrandList(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = BrandSerializer
    filter_backends = (DjangoFilterBackend,
                       SearchFilter,
                       OrderingFilter)
    search_fields = ('name',)
    filter_class = BrandFilter
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class CityView(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class ShopView(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer