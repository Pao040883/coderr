from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrderViewSet, order_count, completed_order_count

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('order-count/<int:business_user_id>/', order_count, name='order-count'),
    path('completed-order-count/<int:business_user_id>/', completed_order_count, name='completed_order_count'),
]