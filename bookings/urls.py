from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'bookings'

router = DefaultRouter()
router.register(r'', views.BookingViewSet, basename='booking')

urlpatterns = [
    # Dashboard endpoints - MUST come before router.urls
    path('dashboard-overview/', views.dashboard_overview, name='dashboard_overview'),
    path('recent-bookings/', views.recent_bookings, name='recent_bookings'),
    path('revenue-chart/', views.revenue_chart, name='revenue_chart'),
    path('villa-performance/', views.villa_performance, name='villa_performance'),
    path('booking-sources/', views.booking_sources, name='booking_sources'),
    # Router URLs (CRUD operations)
    path('', include(router.urls)),
]
