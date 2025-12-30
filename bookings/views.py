from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import date, timedelta
from .models import Booking
from .serializers import BookingSerializer, BookingListSerializer
from villas.models import Villa


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Booking CRUD operations
    """
    queryset = Booking.objects.select_related('villa', 'created_by').all()
    serializer_class = BookingSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        return BookingSerializer
    
    def get_queryset(self):
        queryset = Booking.objects.select_related('villa', 'created_by').all()
        
        # Filtering
        villa_id = self.request.query_params.get('villa', None)
        status_filter = self.request.query_params.get('status', None)
        check_in_after = self.request.query_params.get('check_in_after', None)
        check_in_before = self.request.query_params.get('check_in_before', None)
        search = self.request.query_params.get('search', None)
        
        if villa_id:
            queryset = queryset.filter(villa_id=villa_id)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if check_in_after:
            queryset = queryset.filter(check_in__gte=check_in_after)
        
        if check_in_before:
            queryset = queryset.filter(check_in__lte=check_in_before)
        
        if search:
            queryset = queryset.filter(
                Q(client_name__icontains=search) |
                Q(client_phone__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """
        Get bookings for calendar view
        GET /api/v1/bookings/calendar/?start=YYYY-MM-DD&end=YYYY-MM-DD&villa=ID
        """
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        villa_id = request.query_params.get('villa')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start and end parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Booking.objects.filter(
            check_in__lte=end_date,
            check_out__gte=start_date
        ).select_related('villa')
        
        if villa_id:
            queryset = queryset.filter(villa_id=villa_id)
        
        calendar_data = []
        for booking in queryset:
            calendar_data.append({
                'id': booking.id,
                'villa_id': booking.villa.id,
                'villa_name': booking.villa.name,
                'client_name': booking.client_name,
                'check_in': booking.check_in,
                'check_out': booking.check_out,
                'status': booking.status
            })
        
        return Response(calendar_data)


from rest_framework.decorators import api_view


@api_view(['GET'])
def dashboard_overview(request):
    """
    Get comprehensive dashboard overview
    GET /api/v1/bookings/dashboard-overview/
    """
    from decimal import Decimal
    from django.db.models import Q, Count
    
    reference_date = request.query_params.get('date')
    if reference_date:
        today = date.fromisoformat(reference_date)
    else:
        today = date.today()
    
    # Villa statistics
    total_villas = Villa.objects.count()
    active_villas = Villa.objects.filter(status='active').count()
    maintenance_villas = Villa.objects.filter(status='maintenance').count()
    
    # Today's activity
    today_check_ins = Booking.objects.filter(
        check_in=today,
        status='booked'
    ).count()
    
    today_check_outs = Booking.objects.filter(
        check_out=today,
        status='booked'
    ).count()
    
    # Currently booked villas
    currently_booked = Booking.objects.filter(
        status='booked',
        check_in__lte=today,
        check_out__gt=today
    ).values('villa').distinct().count()
    
    # Occupancy rate (currently booked / total active)
    occupancy_rate = 0
    if active_villas > 0:
        occupancy_rate = round((currently_booked / active_villas) * 100, 1)
    
    # Upcoming bookings (next 7 days)
    next_week = today + timedelta(days=7)
    upcoming_bookings = Booking.objects.filter(
        check_in__gte=today,
        check_in__lte=next_week,
        status='booked'
    ).count()
    
    # This month's statistics
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1)
    
    month_bookings = Booking.objects.filter(
        check_in__gte=month_start,
        check_in__lt=month_end,
        status='booked'
    )
    
    total_bookings_this_month = month_bookings.count()
    revenue_this_month = month_bookings.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    # All-time statistics
    total_bookings = Booking.objects.filter(status='booked').count()
    total_revenue = Booking.objects.filter(status='booked').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    # Average revenue per booking
    avg_revenue = 0
    if total_bookings > 0:
        avg_revenue = float(total_revenue) / total_bookings
    
    return Response({
        'villas': {
            'total': total_villas,
            'active': active_villas,
            'maintenance': maintenance_villas,
            'occupancy_rate': occupancy_rate,
        },
        'today': {
            'check_ins': today_check_ins,
            'check_outs': today_check_outs,
            'currently_booked': currently_booked,
        },
        'bookings': {
            'total': total_bookings,
            'this_month': total_bookings_this_month,
            'upcoming_7_days': upcoming_bookings,
        },
        'revenue': {
            'total': str(total_revenue),
            'this_month': str(revenue_this_month),
            'average_per_booking': round(avg_revenue, 2),
        }
    })


@api_view(['GET'])
def recent_bookings(request):
    """
    Get recent bookings
    GET /api/v1/bookings/recent-bookings/?limit=10
    """
    limit = int(request.query_params.get('limit', 10))
    
    bookings = Booking.objects.select_related('villa').order_by('-created_at')[:limit]
    
    bookings_data = []
    for booking in bookings:
        bookings_data.append({
            'id': booking.id,
            'villa': {
                'id': booking.villa.id,
                'name': booking.villa.name,
            },
            'client_name': booking.client_name,
            'client_phone': booking.client_phone,
            'check_in': booking.check_in,
            'check_out': booking.check_out,
            'status': booking.status,
            'payment_status': booking.payment_status,
            'total_amount': str(booking.total_amount) if booking.total_amount else None,
            'created_at': booking.created_at,
        })
    
    return Response(bookings_data)


@api_view(['GET'])
def revenue_chart(request):
    """
    Get monthly revenue data for charts
    GET /api/v1/bookings/revenue-chart/?months=6
    """
    from decimal import Decimal
    
    months = int(request.query_params.get('months', 6))
    today = date.today()
    
    chart_data = []
    
    for i in range(months - 1, -1, -1):
        # Calculate month
        month_date = today.replace(day=1) - timedelta(days=i * 30)
        month_start = month_date.replace(day=1)
        
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1)
        
        # Get bookings for this month
        month_bookings = Booking.objects.filter(
            check_in__gte=month_start,
            check_in__lt=month_end,
            status='booked'
        )
        
        total_bookings = month_bookings.count()
        total_revenue = month_bookings.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        chart_data.append({
            'month': month_start.strftime('%b %Y'),
            'bookings': total_bookings,
            'revenue': float(total_revenue),
        })
    
    return Response(chart_data)


@api_view(['GET'])
def villa_performance(request):
    """
    Get performance metrics for each villa
    GET /api/v1/bookings/villa-performance/
    """
    from decimal import Decimal
    
    villas = Villa.objects.all()
    performance_data = []
    
    for villa in villas:
        bookings = Booking.objects.filter(villa=villa, status='booked')
        total_bookings = bookings.count()
        
        total_revenue = bookings.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        # Calculate total nights booked
        total_nights = sum([b.nights for b in bookings])
        
        performance_data.append({
            'villa_id': villa.id,
            'villa_name': villa.name,
            'total_bookings': total_bookings,
            'total_revenue': float(total_revenue),
            'total_nights_booked': total_nights,
            'status': villa.status,
        })
    
    # Sort by revenue (highest first)
    performance_data.sort(key=lambda x: x['total_revenue'], reverse=True)
    
    return Response(performance_data)


@api_view(['GET'])
def booking_sources(request):
    """
    Get booking sources breakdown
    GET /api/v1/bookings/booking-sources/
    """
    from django.db.models import Count
    
    # Get count by source
    sources = Booking.objects.filter(
        status='booked'
    ).values('booking_source').annotate(
        count=Count('id')
    ).order_by('-count')
    
    total_bookings = Booking.objects.filter(status='booked').count()
    
    sources_data = []
    for source in sources:
        source_name = source['booking_source'] or 'unknown'
        count = source['count']
        percentage = round((count / total_bookings * 100), 1) if total_bookings > 0 else 0
        
        # Get human-readable name
        source_display = dict(Booking.SOURCE_CHOICES).get(source_name, 'Unknown')
        
        sources_data.append({
            'source': source_name,
            'source_display': source_display,
            'count': count,
            'percentage': percentage,
        })
    
    return Response(sources_data)
