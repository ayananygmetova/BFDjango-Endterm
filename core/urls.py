from django.urls import path

from core.views import category_list, category_detail, BrandList, CityView, ShopView

from rest_framework import routers

router = routers.SimpleRouter()
router.register('brands', BrandList, basename='brands')
router.register('cities', CityView, basename='cities')
router.register('shops', ShopView, basename='shops')


urlpatterns = [
    path('categories/', category_list),
    path('categories/<int:category_id>', category_detail),
]
urlpatterns += router.urls