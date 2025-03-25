from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   path('admin/', admin.site.urls),
   path('api-auth/', include('rest_framework.urls', namespace="rest_framework")),
   path('api/', include('app_user_auth.api.urls')),
   path('api/', include('app_offers.api.urls')),
   path('api/', include('app_orders.api.urls')),
   path('api/', include('app_reviews.api.urls')),
   path('api/', include('app_base_info.api.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)