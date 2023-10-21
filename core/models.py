from django.db import models

from common.validators import validate_file_size, validate_extension


class City(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название города')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Shop(models.Model):
    address = models.CharField(max_length=250, verbose_name='Адрес')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='shop', verbose_name='Город', null=True, blank=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'


class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='children', null=True, blank=True)
    name = models.CharField(verbose_name='Наименование', max_length=100)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class Brand(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=200)
    detail = models.CharField(verbose_name='Описание', max_length=2000, null=True, blank=True)
    image = models.ImageField(upload_to='brand_images', validators=[validate_file_size, validate_extension],
                              null=True, blank=True)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()