from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VillaViewSet, GlobalSpecialDayViewSet

router = DefaultRouter()
router.register(r'villas', VillaViewSet)
router.register(r'special-days', GlobalSpecialDayViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
