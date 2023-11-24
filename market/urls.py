from django.urls import path

from market.views import ApartmentList, DiscountView, RemoveDiscountView, ApartmentReviewView, \
    ApartmentReviewDetailsView, CharacteristicsView, PropertiesView, GroupPropertiesView, ApartmentAvailabilityView

from rest_framework import routers

router = routers.SimpleRouter()
router.register('Apartments', ApartmentList, basename='Apartments')
router.register('characteristics', CharacteristicsView, basename='characteristics')
router.register('properties', PropertiesView, basename='properties')
router.register('group-properties', GroupPropertiesView, basename='group-properties')
router.register('Apartment-availability', ApartmentAvailabilityView, basename='Apartment-availability')


urlpatterns = [
    path('Apartments/set-discount', DiscountView.as_view({'post': 'post'})),
    path('Apartments/remove-discount', RemoveDiscountView.as_view({'post': 'post'})),
    path('Apartments/<int:Apartment_id>/reviews', ApartmentReviewView.as_view({'get': 'list', 'post': 'create'})),
    path('Apartments/<int:Apartment_id>/reviews/<int:review_id>', ApartmentReviewDetailsView.as_view({'delete': 'destroy'})),

]
urlpatterns += router.urls