from django.urls import path

from market.views import ProductList, DiscountView, RemoveDiscountView, ProductReviewView, \
    ProductReviewDetailsView, CharacteristicsView, PropertiesView, GroupPropertiesView, ProductAvailabilityView

from rest_framework import routers

router = routers.SimpleRouter()
router.register('products', ProductList, basename='products')
router.register('characteristics', CharacteristicsView, basename='characteristics')
router.register('properties', PropertiesView, basename='properties')
router.register('group-properties', GroupPropertiesView, basename='group-properties')
router.register('product-availability', ProductAvailabilityView, basename='product-availability')


urlpatterns = [
    path('products/set-discount', DiscountView.as_view({'post': 'post'})),
    path('products/remove-discount', RemoveDiscountView.as_view({'post': 'post'})),
    path('products/<int:product_id>/reviews', ProductReviewView.as_view({'get': 'list', 'post': 'create'})),
    path('products/<int:product_id>/reviews/<int:review_id>', ProductReviewDetailsView.as_view({'delete': 'destroy'})),

]
urlpatterns += router.urls