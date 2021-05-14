
from django.contrib import admin

from payments.models import CreditCard, Order


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction']