from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q

from core.models import Category, Brand
from common.validators import validate_file_size, validate_extension

User = get_user_model()


class GroupProperties(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=200)

    class Meta:
        verbose_name = 'Группа свойств'
        verbose_name_plural = 'Группы свойств'

    def __str__(self):
        return self.name


class Property(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=200)
    group = models.ForeignKey('GroupProperties', verbose_name='Группа', related_name='properties',
                              on_delete=models.SET_NULL, null=True, blank=True)
    detail = models.TextField(verbose_name='Описание', null=True, blank=True)
    is_description = models.BooleanField(verbose_name='Входит в описание', default=False)
    is_filter = models.BooleanField(verbose_name='Фильтр поиска', default=False)

    class Meta:
        verbose_name = 'Свойство'
        verbose_name_plural = 'Свойства'

    def __str__(self):
        return self.name


class ProductCharacteristics(models.Model):
    property = models.ForeignKey(Property, verbose_name='Свойство', related_name='values', on_delete=models.CASCADE)
    value = models.CharField(verbose_name='Значение', max_length=1000)

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товаров'

    def __str__(self):
        return self.property.name + " " + self.value


class ProductReviewManager(models.Manager):

    def users_reviews(self, user_id):
        return ProductReview.objects.filter(user__id=user_id)

    def get_reviews(self, product_id):
        return ProductReview.objects.filter(product__id=product_id)


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', null=True, blank=True)
    review = models.TextField(verbose_name='Отзыв', blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)],
                                 verbose_name='Кол-во звездочек')
    objects = ProductReviewManager()

    class Meta:
        verbose_name = 'Оценивание товара'
        verbose_name_plural = 'Оценивание товаров'
        ordering = ('rating',)


class ProductManager(models.Manager):

    def category_filter(self, category):
        return Product.objects.filter(Q(category=category) |
                                      Q(category__parent=category) |
                                      Q(category__parent__parent=category))

    def set_discounts(self, product_ids, discount):
        products = Product.objects.filter(id__in=product_ids)
        for p in products:
            discount_price = p.real_price - p.real_price * (discount / 100)
            p.current_price = discount_price
            p.discount = discount
            p.save()

    def remove_discounts(self, product_ids):
        for p in Product.objects.filter(id__in=product_ids):
            p.discount = None
            p.current_price = p.real_price
            p.save()

    def discounts(self):
        return Product.objects.filter(discount__isnull=False)


class Product(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=200)
    discount = models.IntegerField(verbose_name='Скидка', null=True, blank=True)
    current_price = models.IntegerField(verbose_name='Текущая цена')
    real_price = models.IntegerField(verbose_name='Настоящая цена', default='current_price')
    image = models.ImageField(upload_to='product_images', validators=[validate_file_size, validate_extension],
                              null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', verbose_name='Категория товара',
                                 on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, related_name='products', verbose_name='Бренд', on_delete=models.SET_NULL,
                              null=True, blank=True)
    characteristics = models.ManyToManyField(ProductCharacteristics, verbose_name='Характеристики',
                                             related_name='product', null=True, blank=True)
    reviews = models.ManyToManyField(ProductReview, verbose_name='Оценивание товара', null=True, blank=True,
                                     related_name='product')
    is_recommended = models.BooleanField(verbose_name='Рекомендованный', default=False)
    is_popular = models.BooleanField(verbose_name='Популярный', default=False)
    is_new = models.BooleanField(verbose_name='Новинка', default=False)
    objects = ProductManager()

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    @property
    def rating(self):
        reviews = self.reviews.all()
        if reviews.count() == 0:
            return 0
        data = reviews.aggregate(sum_points=models.Sum('rating'))
        overall_rating = data['sum_points'] / reviews.count()
        return "{:.2f}".format(overall_rating)


class ProductUnit(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True,
                                verbose_name='Товар')
    amount = models.IntegerField(verbose_name='Количество товаров')

    class Meta:
        abstract = True


class ProductAvailability(ProductUnit):
    shop = models.ForeignKey('core.Shop', on_delete=models.CASCADE, related_name='avalability', verbose_name='Магазин')

    class Meta:
        verbose_name = 'Наличие товара'
        verbose_name_plural = 'Наличие товаров'
