from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework import routers

from auth_.views import UsersView, LogoutView, RegisterView, CurrentCityView, ChangeDetailsView

router = routers.SimpleRouter()
router.register('users', UsersView, basename='users')

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('change-details/', ChangeDetailsView.as_view(), name='change-details'),
    path('cur-city/', CurrentCityView.as_view(), name='cur_city')
]
urlpatterns += router.urls