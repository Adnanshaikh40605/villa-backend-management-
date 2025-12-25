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


@action(detail=False, methods=['get'])
def dashboard_stats(request):
    """
    Get dashboard statistics
    GET /api/v1/dashboard/stats/?date=YYYY-MM-DD
    """
    reference_date = request.query_params.get('date')
    if reference_date:
        today = date.fromisoformat(reference_date)
    else:
        today = date.today()
    
    # Total villas
    total_villas = Villa.objects.count()
    active_villas = Villa.objects.filter(status='active').count()
    maintenance_villas = Villa.objects.filter(status='maintenance').count()
    
    # Today's check-ins and check-outs
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
    
    # Upcoming bookings (next 7 days)
    next_week = today + timedelta(days=7)
    upcoming_bookings = Booking.objects.filter(
        check_in__gte=today,
        check_in__lte=next_week
    ).count()
    
    # This month's bookings and revenue
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
    )['total'] or 0
    
    return Response({
        'total_villas': total_villas,
        'active_villas': active_villas,
        'maintenance_villas': maintenance_villas,
        'today_check_ins': today_check_ins,
        'today_check_outs': today_check_outs,
        'currently_booked': currently_booked,
        'upcoming_bookings_7_days': upcoming_bookings,
        'total_bookings_this_month': total_bookings_this_month,
        'revenue_this_month': str(revenue_this_month)
    })


@action(detail=False, methods=['get'])
def today_activity(request):
    """
    Get today's check-ins and check-outs
    GET /api/v1/dashboard/today-activity/
    """
    today = date.today()
    
    check_ins = Booking.objects.filter(
        check_in=today,
        status='booked'
    ).select_related('villa')
    
    check_outs = Booking.objects.filter(
        check_out=today,
        status='booked'
    ).select_related('villa')
    
    check_ins_data = []
    for booking in check_ins:
        check_ins_data.append({
            'id': booking.id,
            'villa': {
                'id': booking.villa.id,
                'name': booking.villa.name
            },
            'client_name': booking.client_name,
            'client_phone': booking.client_phone,
            'number_of_guests': booking.number_of_guests
        })
    
    check_outs_data = []
    for booking in check_outs:
        check_outs_data.append({
            'id': booking.id,
            'villa': {
                'id': booking.villa.id,
                'name': booking.villa.name
            },
            'client_name': booking.client_name,
            'client_phone': booking.client_phone,
            'number_of_guests': booking.number_of_guests
        })
    
    return Response({
        'check_ins': check_ins_data,
        'check_outs': check_outs_data
    })
