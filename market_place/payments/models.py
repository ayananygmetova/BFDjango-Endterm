from django.core.validators import MinValueValidator
from django.db import models

from common.constants import DONT_ENOUGH_MONEY, MONEY_ENOUGH, ORDER_STATUSES, AVAILABLE, DONT_AVAILABLE
from common.utils import random_nums, random_csv
from market.models import ProductAvailability, ProductUnit


class CreditCard(models.Model):
    user = models.OneToOneField('auth_.User', on_delete=models.CASCADE, related_name='credit_card',
                                verbose_name='Владелец')
    numbers = models.FloatField(verbose_name='Номер карты', default=random_nums, unique=True)
    valid_thru = models.DateField(verbose_name='Срок действия')
    csv = models.IntegerField(verbose_name='Код карты', default=random_csv)
    balance = models.IntegerField(validators=[MinValueValidator(0)], verbose_name='Остаток средств', default=0)

    class Meta:
        verbose_name = 'Кредитная карта'
        verbose_name_plural = 'Кредитные карты'


class CartItem(ProductUnit):
    class Meta:
        verbose_name = 'Объект корзины'
        verbose_name_plural = 'Объекты корзины'


class CartManager(models.Manager):
    def personal(self, user):
        return Cart.objects.get(user=user)

    def add_product(self, user, product_id, amount):
        from market.models import Product
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.personal(user=user)
        item = cart.cart_items.filter(product=product).first()
        if item:
            item.amount = amount
            item.save()
        else:
            item = CartItem.objects.create(product=product, amount=amount)
            cart.cart_items.add(item)
            cart.save()

    def remove_product(self, user, product_id):
        from market.models import Product
        Product.objects.get(id=product_id)
        cart = Cart.objects.personal(user=user)
        item = cart.cart_items.filter(product__id=product_id).first()
        cart.cart_items.remove(item)
        cart.save()


class Cart(models.Model):
    user = models.ForeignKey('auth_.User', on_delete=models.CASCADE, verbose_name='Пользователь', related_name='cart')
    cart_items = models.ManyToManyField(CartItem, related_name='cart', verbose_name='Объекты корзины')
    total_sum = models.IntegerField(default=0, verbose_name='Сумма')
    objects = CartManager()

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'

    @property
    def total_sum(self):
        sum = 0
        for item in self.cart_items.all():
            sum_item = item.amount * item.product.current_price
            sum += sum_item
        self.total_sum = sum
        self.save()
        return sum

    def check_balance(self):
        card = self.user.credit_card
        if card:
            if card.balance >= self.total_sum:
                return MONEY_ENOUGH
            return DONT_ENOUGH_MONEY

    def withdraw_money(self):
        card = self.user.credit_card
        if card:
            card.balance -= self.total_sum
            card.save()

    def empty_cart(self):
        self.cart_items.all().delete()

    def check_availability(self):
        city = self.user.cur_city
        items = self.cart_items.all()
        for item in items:
            available = ProductAvailability.objects.filter(shop__city=city)
            product_items = available.filter(product=item.product, amount__gte=item.amount)
            if not product_items:
                return (DONT_AVAILABLE, item.product.name)
        return (AVAILABLE, '')

    @total_sum.setter
    def total_sum(self, value):
        self._total_sum = value


class Transaction(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='transaction', verbose_name='Корзина',
                             null=True, blank=True)
    date_created = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'


class OrderManager(models.Manager):
    def user_orders(self, user):
        return Order.objects.filter(transaction__cart__user=user)

    def assignee_orders(self, assignee):
        return Order.objects.filter(assignee=assignee)


class Order(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='order',
                                    verbose_name='Транзакция')
    status = models.CharField(choices=ORDER_STATUSES, default='NOT_ASSIGNED', verbose_name='Cтатус', max_length=150)
    assignee = models.ForeignKey('auth_.User', on_delete=models.SET_NULL, related_name='orders', null=True,
                                 blank=True, verbose_name='Исполнитель')
    objects = OrderManager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'