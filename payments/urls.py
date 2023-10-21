from django.urls import path
from rest_framework import routers

from payments.views import CreditCardView, OrderView, CartView, CardDetails, TransactionView

router = routers.SimpleRouter()
router.register('credit-card', CreditCardView, basename='credit-card')
router.register('orders', OrderView, basename='orders')
router.register('transaction', TransactionView, basename='transactions')

urlpatterns = [
    path('cart/', CartView.as_view()),
    path('cart/details/', CardDetails.as_view())
]

urlpatterns += router.urls