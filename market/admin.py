from django.contrib import admin

from market.models import Apartment, ApartmentCharacteristics, Property, GroupProperties


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_price', 'category', 'brand']
    ordering = ['name', 'current_price']
    search_fields = ['name', 'current_price', 'category', ]
    list_filter = ['current_price' ]


@admin.register(ApartmentCharacteristics)
class ApartmentCharacteristicsAdmin(admin.ModelAdmin):
    list_display = ['property', 'value']
    ordering = ['property']
    search_fields = ['property', 'value']
    list_filter = ['property', 'value', ]


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'group']
    ordering = ['name']
    search_fields = ['name', 'group', ]
    list_filter = ['name']


@admin.register(GroupProperties)
class GroupPropertiesAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ['name']
    search_fields = ['name']
    list_filter = ['name']