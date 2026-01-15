from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router configuration

app_name = 'bookings'

router = DefaultRouter()
router.register(r'', views.BookingViewSet, basename='booking')

urlpatterns = [
    # Dashboard endpoints - MUST come before router.urls
    path('dashboard-overview/', views.dashboard_overview, name='dashboard_overview'),
    path('recent-bookings/', views.recent_bookings, name='recent_bookings'),
    path('revenue-chart/', views.revenue_chart, name='revenue_chart'),
    path('villa-performance/', views.villa_performance, name='villa_performance'),
    path('revenue-candles/', views.revenue_candles, name='revenue_candles'),
    # Explicitly register calculate-price to avoid router issues - MOVED TO CONFIG/URLS.PY
    # path('calculate-price/', views.calculate_price_view, name='calculate-price'),
    
    path('send-email-confirmation/<int:pk>/', views.send_email_confirmation, name='send-email-confirmation'),
    
    # Router URLs (CRUD operations)
    path('', include(router.urls)),
]
