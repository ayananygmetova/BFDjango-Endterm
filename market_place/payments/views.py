import json

from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import ManagerPermission
from common.constants import CANCELED, DONE, DONT_ENOUGH_MONEY, DONT_AVAILABLE
from payments.models import CreditCard, Order, Cart
from payments.serializers import CreditCardSerializer, OrderSerializer, TransactionSerializer, CartSerializer

import logging

logger = logging.getLogger(__name__)


class CreditCardView(viewsets.ViewSet, mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        logger.info(f'create credit card: {request.data}')
        data = request.data
        data['user'] = request.user.pk
        serializer = CreditCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'create credit card: {request.data} - {str(serializer.errors)}')
        return Response({'error': serializer.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        try:
            logger.info('get cart')
            cart = Cart.objects.personal(user=request.user)
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'get cart - {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info('post items to cart')
            data = json.loads(request.body)
            Cart.objects.add_product(user=request.user, product_id=data['product_id'], amount=data.get('amount', 1))
            return Response({'info': 'added'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"post item to cart - str(e)")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CardDetails(APIView):
    def post(self, request):
        try:
            logger.info(f'delete item from cart {str(request.data)}')
            data = json.loads(request.body)
            Cart.objects.remove_product(user=request.user, product_id=data['product_id'])
            return Response({'info': 'deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'delete item from cart {str(request.data)} - {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionView(viewsets.ViewSet, mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated, )

    def create(self, request):
        try:
            logger.info(f'create transaction: {request.data}')
            cart = Cart.objects.get(user=request.user)
            card = CreditCard.objects.get(user=request.user)
            has_balance = cart.check_balance()
            if has_balance == DONT_ENOUGH_MONEY:
                raise Exception('У вас недостаточно средств на карте')
            is_available = cart.check_availability()
            if is_available[0] == DONT_AVAILABLE:
                raise Exception(f'Данных товаров нет в наличии {is_available[1]}')
            data = {"cart": cart.id}
            serializer = TransactionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                cart.withdraw_money()
                cart.empty_cart()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except CreditCard.DoesNotExist:
            logger.error(f'create transaction: {request.data} - credit card doesn\'t exist')
            return Response({"error": "Нет кредитной карты! Добавьте ее"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f'create transaction: {request.data} - {str(e)}')
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(methods=['GET'], detail=False, url_path='managers', url_name='managers',
            permission_classes=(ManagerPermission,))
    def managers_orders(self, request):
        logger.info(f'managers\' orders')
        queryset = Order.objects.assignee_orders(assignee=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='all', url_name='all',
            permission_classes=(ManagerPermission,))
    def all_orders(self, request):
        logger.info(f'all orders')
        queryset = Order.objects.all()
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['PUT'], detail=True, url_path='cancel', url_name='cancel',
            permission_classes=(IsAuthenticated,))
    def user_cancel(self, request, pk):
        logger.info('user cancel order')
        order = Order.objects.get(id=pk)
        order.status = CANCELED
        order.assignee = None
        order.save()
        return Response({'info': 'canceled'}, status=status.HTTP_200_OK)

    @action(methods=['PUT'], detail=True, url_path='complete', url_name='complete',
            permission_classes=(ManagerPermission,))
    def complete_order(self, request, pk):
        logger.info(f'order completed {pk}')
        order = Order.objects.get(id=pk)
        order.status = DONE
        order.save()
        return Response({'info': 'completed'}, status=status.HTTP_200_OK)