from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferView, OfferDetailView

# Router erstellen
router = DefaultRouter()
router.register(r'offers', OfferView, basename='offer')

urlpatterns = [
    path('', include(router.urls)), 
    path('offerdetails/<int:pk>/', OfferDetailView.as_view(), name='offerdetails') 
]