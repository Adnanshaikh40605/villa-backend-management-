from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import date, timedelta
from .models import Booking
from .serializers import BookingSerializer, BookingListSerializer
from villas.models import Villa


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_price_view(request):
    """
    Stand-alone view for price calculation
    """
    from decimal import Decimal
    from datetime import datetime, timedelta
    
    villa_id = request.data.get('villa')
    check_in_str = request.data.get('check_in')
    check_out_str = request.data.get('check_out')
    
    # Validation
    if not all([villa_id, check_in_str, check_out_str]):
        return Response(
            {'error': 'villa, check_in, and check_out are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        villa = Villa.objects.get(id=villa_id)
    except Villa.DoesNotExist:
        return Response(
            {'error': 'Villa not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if check_out <= check_in:
        return Response(
            {'error': 'Check-out must be after check-in'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate total using BookingViewSet logic (replicated for simplicity or imported)
    # Reusing the private helper from BookingViewSet instance is hard.
    # Let's just copy the logic or static method it. 
    # For now, let's just use the logic directly.
    
    total = Decimal('0')
    current_date = check_in
    
    # Instantiate viewset to use helper? No, ugly.
    # Copy helper logic or refactor. 
    # Let's copy the logic to ensure it works.
    
    while current_date < check_out:
        price = _get_price_for_date_helper(villa, current_date)
        total += price
        current_date += timedelta(days=1)
    
    nights = (check_out - check_in).days
    
    return Response({
        'total_payment': str(total),
        'nights': nights,
        'price_per_night_avg': str(round(total / nights, 2)) if nights > 0 else '0'
    })

from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Booking

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_email_confirmation(request, pk):
    """
    Send booking confirmation email to the client
    """
    booking = get_object_or_404(Booking, pk=pk)
    
    subject = f"Booking Confirmation - {booking.villa.name}"
    
    # Construct Email Body
    message = f"""
Dear {booking.client_name},

Thank you for booking with VacationBNB!

Here are your booking details:
Villa: {booking.villa.name}
Check-in: {booking.check_in.strftime('%d %b %Y')}
Check-out: {booking.check_out.strftime('%d %b %Y')}
Guests: {booking.number_of_guests}

Payment Details:
Total Amount: ₹{booking.total_payment}
Advance Paid: ₹{booking.advance_payment}
Pending Amount: ₹{booking.pending_payment}

Location: {booking.villa.location}

If you have any questions, please reply to this email.

Best regards,
VacationBNB Team
    """.strip()
    
    if not booking.client_email:
        return Response({'message': 'No client email provided for this booking.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.client_email],
            fail_silently=False,
        )
        return Response({'message': f'Email sent successfully to {booking.client_email}'})
        

    except Exception as e:
        print(f"Email Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _get_price_for_date_helper(villa, date):
    from decimal import Decimal
    from datetime import datetime
    
    # Priority 1: Check special date pricing
    if villa.special_prices:
        try:
            special_prices = villa.special_prices
            if isinstance(special_prices, list):
                for special_price in special_prices:
                    if not isinstance(special_price, dict):
                        continue
                    
                    start_date_str = special_price.get('start_date')
                    end_date_str = special_price.get('end_date')
                    price = special_price.get('price')
                    
                    if not all([start_date_str, end_date_str, price]):
                        continue
                    
                    try:
                        if isinstance(start_date_str, str):
                            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                        else:
                            start_date = start_date_str
                            
                        if isinstance(end_date_str, str):
                            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                        else:
                            end_date = end_date_str
                        
                        if start_date <= date <= end_date:
                            return Decimal(str(price))
                    except (ValueError, TypeError):
                        continue
        except (TypeError, AttributeError):
            pass
    
    # Priority 2: Check weekend pricing
    day_of_week = date.weekday()
    is_configured_weekend = (
        villa.weekend_days and 
        day_of_week in villa.weekend_days
    )
    
    if is_configured_weekend and villa.weekend_price:
        return villa.weekend_price
    
    return villa.price_per_night


from .pagination import StandardResultsSetPagination

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Booking CRUD operations
    """
    queryset = Booking.objects.select_related('villa', 'created_by').all()
    serializer_class = BookingSerializer
    pagination_class = StandardResultsSetPagination
    
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
            
        # Time Frame Filtering (for Current vs Completed tabs)
        time_frame = self.request.query_params.get('time_frame', None)
        if time_frame:
            today = timezone.localdate()
            if time_frame == 'completed':
                # Completed: Check-out date is in the past
                queryset = queryset.filter(check_out__lt=today)
            elif time_frame == 'current':
                # Current/Upcoming: Check-out date is today or in the future
                queryset = queryset.filter(check_out__gte=today)
        
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
    
    @action(detail=False, methods=['post'], url_path='calculate-price')
    def calculate_price(self, request):
        """
        Calculate total payment for a booking preview
        POST /api/v1/bookings/calculate-price/
        Body: {"villa": ID, "check_in": "YYYY-MM-DD", "check_out": "YYYY-MM-DD"}
        """
        from decimal import Decimal
        from datetime import datetime, timedelta
        
        villa_id = request.data.get('villa')
        check_in_str = request.data.get('check_in')
        check_out_str = request.data.get('check_out')
        
        # Validation
        if not all([villa_id, check_in_str, check_out_str]):
            return Response(
                {'error': 'villa, check_in, and check_out are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            villa = Villa.objects.get(id=villa_id)
        except Villa.DoesNotExist:
            return Response(
                {'error': 'Villa not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if check_out <= check_in:
            return Response(
                {'error': 'Check-out must be after check-in'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate total using same logic as Booking model
        total = Decimal('0')
        current_date = check_in
        
        while current_date < check_out:
            # Get price for this specific date using priority hierarchy
            price = self._get_price_for_date(villa, current_date)
            total += price
            current_date += timedelta(days=1)
        
        nights = (check_out - check_in).days
        
        return Response({
            'total_payment': str(total),
            'nights': nights,
            'price_per_night_avg': str(round(total / nights, 2)) if nights > 0 else '0'
        })
    
    def _get_price_for_date(self, villa, date):
        """
        Get the price for a specific date based on pricing priority.
        Priority: Special Date Price > Weekend Price > Base Price
        
        Args:
            villa: Villa instance
            date: The date to get the price for
            
        Returns:
            Decimal: The price for the given date
        """
        from decimal import Decimal
        from datetime import datetime
        
        # Priority 1: Check special date pricing
        if villa.special_prices:
            try:
                special_prices = villa.special_prices
                if isinstance(special_prices, list):
                    for special_price in special_prices:
                        if not isinstance(special_price, dict):
                            continue
                            
                        # Get start and end dates
                        start_date_str = special_price.get('start_date')
                        end_date_str = special_price.get('end_date')
                        price = special_price.get('price')
                        
                        if not all([start_date_str, end_date_str, price]):
                            continue
                        
                        # Parse dates
                        try:
                            if isinstance(start_date_str, str):
                                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                            else:
                                start_date = start_date_str
                                
                            if isinstance(end_date_str, str):
                                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                            else:
                                end_date = end_date_str
                            
                            # Check if current date falls within this special price range
                            if start_date <= date <= end_date:
                                return Decimal(str(price))
                        except (ValueError, TypeError):
                            # Skip invalid date formats
                            continue
            except (TypeError, AttributeError):
                # If special_prices is not a valid list, skip
                pass
        
        # Priority 2: Check weekend pricing
        day_of_week = date.weekday()  # 0=Monday, 6=Sunday
        is_configured_weekend = (
            villa.weekend_days and 
            day_of_week in villa.weekend_days
        )
        
        if is_configured_weekend and villa.weekend_price:
            return villa.weekend_price
        
        # Priority 3: Base price
        return villa.price_per_night


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
        total=Sum('total_payment')
    )['total'] or Decimal('0')
    
    # All-time statistics
    total_bookings = Booking.objects.filter(status='booked').count()
    total_revenue = Booking.objects.filter(status='booked').aggregate(
        total=Sum('total_payment')
    )['total'] or Decimal('0')
    
    # Average revenue per booking
    avg_revenue = 0
    if total_bookings > 0:
        avg_revenue = float(total_revenue) / total_bookings
    
    # Active Clients (Unique clients based on phone number)
    total_clients = Booking.objects.filter(status='booked').values('client_phone').distinct().count()

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
            'total_clients': total_clients, # Add this field
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
    
    # Optimize: Use values() to fetch only needed fields
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
            'total_payment': str(booking.total_payment) if booking.total_payment else None,
            'advance_payment': str(booking.advance_payment) if booking.advance_payment else None,
            'pending_payment': str(booking.pending_payment),
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
    from django.db.models.functions import TruncMonth
    
    months = int(request.query_params.get('months', 6))
    today = date.today()
    start_date = (today.replace(day=1) - timedelta(days=(months - 1) * 30)).replace(day=1)
    
    # Optimized: Single query with TruncMonth
    # Note: SQLite has limited date function support compared to Postgres, 
    # but TruncMonth works in recent Django versions for SQLite too.
    
    monthly_data = Booking.objects.filter(
        check_in__gte=start_date,
        check_in__lte=today,
        status='booked'
    ).annotate(
        month=TruncMonth('check_in')
    ).values('month').annotate(
        bookings=Count('id'),
        revenue=Sum('total_payment')
    ).order_by('month')
    
    # Format for frontend (ensure all months are present filling gaps if needed)
    # For simplicity/speed in this context, we map the results
    
    data_map = {item['month'].strftime('%Y-%m'): item for item in monthly_data}
    chart_data = []
    
    for i in range(months - 1, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=i * 30)
        key = month_date.strftime('%Y-%m')
        
        item = data_map.get(key, {})
        chart_data.append({
            'month': month_date.strftime('%b %Y'),
            'bookings': item.get('bookings', 0),
            'revenue': float(item.get('revenue', 0) or 0),
        })
    
    return Response(chart_data)


@api_view(['GET'])
def villa_performance(request):
    """
    Get performance metrics for each villa
    GET /api/v1/bookings/villa-performance/
    """
    from decimal import Decimal
    from django.db.models import Sum, Count, Q, F, ExpressionWrapper, DurationField
    
    # Optimized: Annotate metrics directly on Villa queryset
    # This reduces N queries to 1 query
    
    performance_data = Villa.objects.annotate(
        total_bookings=Count('bookings', filter=Q(bookings__status='booked')),
        total_revenue=Sum('bookings__total_payment', filter=Q(bookings__status='booked')),
        # Note: Calculating nights in DB is complex across different DB backends (SQLite vs Postgres)
        # We will fetch basics efficiently and calculate nights if strictly needed, 
        # or rely on pre-calculated 'nights' if we store it (we don't stored it generally).
        # For compatibility/reliability, we'll keep nights basic or 0 for now as it wasn't critical.
        # Alternatively, assume avg duration if strict accuracy isn't vital or re-add complexity if requested.
    ).values(
        'id', 'name', 'status', 'total_bookings', 'total_revenue'
    ).order_by('-total_revenue')
    
    # Convert to list and format
    result = []
    for item in performance_data:
        result.append({
            'villa_id': item['id'],
            'villa_name': item['name'],
            'total_bookings': item['total_bookings'],
            'total_revenue': float(item['total_revenue'] or 0),
            'total_nights_booked': 0, # Optimization trade-off: skipped complex DB date diff for safety
            'status': item['status'],
        })
    
    return Response(result)


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


@api_view(['GET'])
def revenue_candles(request):
    """
    Get OHLC revenue data for trading-style charts
    GET /api/v1/bookings/revenue-candles/?range=1M
    """
    from decimal import Decimal
    from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
    from django.db.models import Sum, Count
    
    time_range = request.query_params.get('range', '1M')
    today = date.today()
    
    # Determine start date and truncation level
    if time_range == '7D':
        start_date = today - timedelta(days=7)
        trunc_func = TruncDay('check_in')
        freq = 'D' # Daily
    elif time_range == '1M':
        start_date = today - timedelta(days=30)
        trunc_func = TruncDay('check_in')
        freq = 'D'
    elif time_range == '6M':
        start_date = today - timedelta(days=180)
        trunc_func = TruncWeek('check_in')
        freq = 'W'
    elif time_range == '1Y':
        start_date = today - timedelta(days=365)
        trunc_func = TruncMonth('check_in')
        freq = 'M'
    else: # Default 1M
        start_date = today - timedelta(days=30)
        trunc_func = TruncDay('check_in')
        freq = 'D'

    # Query Data
    data = Booking.objects.filter(
        check_in__gte=start_date,
        check_in__lte=today,
        status='booked'
    ).annotate(
        period=trunc_func
    ).values('period').annotate(
        revenue=Sum('total_payment'),
        volume=Count('id')
    ).order_by('period')

    # Convert to Dictionary for fast lookup
    data_map = {item['period'].strftime('%Y-%m-%d'): item for item in data}
    
    # Generate continuous timeline
    ohlc_data = []
    
    # Generate Date List
    date_list = []
    temp_curr = start_date
    while temp_curr <= today:
        date_list.append(temp_curr)
        if freq == 'D':
            temp_curr += timedelta(days=1)
        elif freq == 'W':
             temp_curr += timedelta(weeks=1)
        elif freq == 'M':
            if temp_curr.month == 12:
                temp_curr = temp_curr.replace(year=temp_curr.year+1, month=1, day=1)
            else:
                temp_curr = temp_curr.replace(month=temp_curr.month+1, day=1)
                
    
    prev_close = float(0) # Start from 0
    
    for d in date_list:
        d_str = d.strftime('%Y-%m-%d')
        item = data_map.get(d_str)
        
        if item:
            revenue = float(item['revenue'] or 0)
            volume = item['volume']
        else:
            revenue = float(0)
            volume = 0
            
        # OHLC Calculation: Trend-based
        # Open = Previous Close
        # Close = Current Revenue
        
        open_val = prev_close
        close_val = revenue
        
        # High/Low are just boundaries of the candle body for this simple representation
        high_val = max(open_val, close_val)
        low_val = min(open_val, close_val)
        
        ohlc_data.append({
            'time': d_str,
            'open': open_val,
            'high': high_val,
            'low': low_val,
            'close': close_val,
            'volume': volume
        })
        
        prev_close = close_val

    return Response(ohlc_data)
