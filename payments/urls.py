from django.urls import path
from rest_framework import routers

from payments.views import CreditCardView, OrderView, favoriteView, CardDetails, TransactionView

router = routers.SimpleRouter()
router.register('credit-card', CreditCardView, basename='credit-card')
router.register('orders', OrderView, basename='orders')
router.register('transaction', TransactionView, basename='transactions')

urlpatterns = [
    path('favorite/', favoriteView.as_view()),
    path('favorite/details/', CardDetails.as_view())
]

urlpatterns += router.urls