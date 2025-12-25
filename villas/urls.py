from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'villas'

router = DefaultRouter()
router.register(r'', views.VillaViewSet, basename='villa')

urlpatterns = [
    path('', include(router.urls)),
]
