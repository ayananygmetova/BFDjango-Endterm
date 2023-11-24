from django.core.validators import MinValueValidator
from django.db import models

from common.constants import DONT_ENOUGH_MONEY, MONEY_ENOUGH, ORDER_STATUSES, AVAILABLE, DONT_AVAILABLE
from common.utils import random_nums, random_csv
from market.models import ApartmentAvailability, ApartmentUnit


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


class favoriteItem(ApartmentUnit):
    class Meta:
        verbose_name = 'Объект корзины'
        verbose_name_plural = 'Объекты корзины'


class favoriteManager(models.Manager):
    def personal(self, user):
        return Favorite.objects.get(user=user)

    def add_apartment(self, user, Apartment_id, amount):
        from market.models import Apartment
        Apartment = Apartment.objects.get(id=Apartment_id)
        favorite = Favorite.objects.personal(user=user)
        item = favorite.favorite_items.filter(Apartment=Apartment).first()
        if item:
            item.amount = amount
            item.save()
        else:
            item = favoriteItem.objects.create(Apartment=Apartment, amount=amount)
            favorite.favorite_items.add(item)
            favorite.save()

    def remove_apartment(self, user, Apartment_id):
        from market.models import Apartment
        Apartment.objects.get(id=Apartment_id)
        favorite = Favorite.objects.personal(user=user)
        item = favorite.favorite_items.filter(Apartment__id=Apartment_id).first()
        favorite.favorite_items.remove(item)
        favorite.save()


class Favorite(models.Model):
    user = models.ForeignKey('auth_.User', on_delete=models.CASCADE, verbose_name='Пользователь', related_name='favorite',
                             null=True, blank=True)
    favorite_items = models.ManyToManyField(favoriteItem, related_name='favorite', verbose_name='Объекты корзины')
    total_sum = models.IntegerField(default=0, verbose_name='Сумма')
    objects = favoriteManager()

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'

    @property
    def total_sum(self):
        sum = 0
        for item in self.favorite_items.all():
            sum_item = item.amount * item.Apartment.current_price
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

    def empty_favorite(self):
        for item in self.favorite_items.all():
            self.favorite_items.remove(item)
        self.save()

    def check_availability(self):
        city = self.user.cur_city
        items = self.favorite_items.all()
        available = ApartmentAvailability.objects.filter(shop__city=city)
        for a in available:
            has_apartments = True
            for item in items:
                Apartment_items = available.filter(Apartment=item.Apartment, amount__gte=item.amount)
                if not Apartment_items:
                    has_apartments = False
            if has_apartments:
                return (AVAILABLE,a.id)
        return (DONT_AVAILABLE, '')


    @total_sum.setter
    def total_sum(self, value):
        self._total_sum = value


class Transaction(models.Model):
    favorite = models.ForeignKey('favorite', on_delete=models.CASCADE, related_name='transaction', verbose_name='Корзина',
                             null=True, blank=True)
    date_created = models.DateTimeField(auto_now=True, verbose_name='Дата создания')
    availability = models.ForeignKey('market.ApartmentAvailability', on_delete=models.SET_NULL, related_name='transaction',
                                     verbose_name='Наличие товара', null=True, blank=True)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'


class OrderManager(models.Manager):
    def user_orders(self, user):
        return Order.objects.filter(transaction__favorite__user=user)

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