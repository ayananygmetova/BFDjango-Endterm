from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('auth_.urls')),
    path('core/', include('core.urls')),
    path('market/', include('market.urls')),
    path('payments/', include('payments.urls'))
]