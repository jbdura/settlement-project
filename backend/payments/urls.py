# payments/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MerchantViewSet, PaymentViewSet,
    FeeViewSet, SettlementViewSet
)

router = DefaultRouter()
router.register(r'merchants', MerchantViewSet, basename='merchant')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'fees', FeeViewSet, basename='fee')
router.register(r'settlements', SettlementViewSet, basename='settlement')

urlpatterns = [
    path('api/', include(router.urls)),
]
