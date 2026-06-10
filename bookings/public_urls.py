from django.urls import path

from . import public_views

urlpatterns = [
    path('availability/', public_views.public_availability, name='public-availability'),
]
