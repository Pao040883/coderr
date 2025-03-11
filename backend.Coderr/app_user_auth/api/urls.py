from django.urls import path
from .views import ProfileViewSet, BusinessProfileListView, CustomerProfileListView, RegistrationView, LoginView

urlpatterns = [
    path("profile/<int:pk>/", ProfileViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="profile-detail"),
    path("profiles/business/", BusinessProfileListView.as_view(), name="business-profiles"),
    path("profiles/customer/", CustomerProfileListView.as_view(), name="customer-profiles"),
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
]
