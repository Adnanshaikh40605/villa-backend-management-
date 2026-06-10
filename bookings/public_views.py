"""
Public availability API — no authentication required.
Returns only villa names and date-level status (available / booked / blocked).
No client names, prices, or other sensitive booking data.
"""
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from bookings.models import Booking
from villas.models import GlobalSpecialDay, Villa
from villas.public_holidays import (
    build_calendar_day_info,
    list_special_days_for_response,
)

MAX_RANGE_DAYS = 93

DEFAULT_PRICING = {
    'weekday_three_bhk': 8000,
    'weekday_four_bhk': 10000,
    'weekend_three_bhk': 9000,
    'weekend_four_bhk': 10000,
    'extra_per_person': 500,
    'special_day_three_bhk': 10000,
    'special_day_four_bhk': 12000,
}


def _get_bhk_type(name: str) -> str | None:
    upper = name.upper()
    if '4BHK' in upper or '4 BHK' in upper:
        return '4bhk'
    if '3BHK' in upper or '3 BHK' in upper:
        return '3bhk'
    return None


def _short_villa_name(name: str) -> str:
    """First meaningful word for compact mobile headers."""
    parts = name.strip().split()
    return parts[0].title() if parts else name


def _compute_pricing(villas) -> dict:
    pricing = dict(DEFAULT_PRICING)
    for villa in villas:
        bhk = _get_bhk_type(villa.name)
        weekday = int(villa.price_per_night)
        weekend = int(villa.weekend_price) if villa.weekend_price else weekday
        if bhk == '3bhk':
            pricing['weekday_three_bhk'] = weekday
            pricing['weekend_three_bhk'] = weekend
            if villa.special_day_price:
                pricing['special_day_three_bhk'] = int(villa.special_day_price)
        elif bhk == '4bhk':
            pricing['weekday_four_bhk'] = weekday
            pricing['weekend_four_bhk'] = weekend
            if villa.special_day_price:
                pricing['special_day_four_bhk'] = int(villa.special_day_price)
    return pricing


def _status_for_date(villa_id, day, bookings_by_villa) -> str:
    for booking in bookings_by_villa.get(villa_id, []):
        if booking.check_in <= day < booking.check_out:
            return booking.status if booking.status == 'blocked' else 'booked'
    return 'available'


@api_view(['GET'])
@permission_classes([AllowAny])
def public_availability(request):
    """
    GET /api/v1/public/availability/?start=YYYY-MM-DD&end=YYYY-MM-DD

    Public read-only availability for customers.
    """
    start_str = request.query_params.get('start')
    end_str = request.query_params.get('end')

    if not start_str or not end_str:
        return Response(
            {'error': 'start and end query parameters are required (YYYY-MM-DD)'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if end_date < start_date:
        return Response(
            {'error': 'end must be on or after start'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if (end_date - start_date).days > MAX_RANGE_DAYS:
        return Response(
            {'error': f'Date range cannot exceed {MAX_RANGE_DAYS} days'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    villas = list(Villa.objects.filter(status='active').order_by('order', 'name'))
    villa_ids = [v.id for v in villas]

    bookings = Booking.objects.filter(
        villa_id__in=villa_ids,
        check_in__lte=end_date,
        check_out__gt=start_date,
    ).only('villa_id', 'check_in', 'check_out', 'status')

    bookings_by_villa: dict[int, list] = {}
    for booking in bookings:
        bookings_by_villa.setdefault(booking.villa_id, []).append(booking)

    global_special_days = list(GlobalSpecialDay.objects.all())
    special_days_payload = list_special_days_for_response(global_special_days)
    days_payload = build_calendar_day_info(start_date, end_date, global_special_days)

    villas_payload = []
    for villa in villas:
        availability = {}
        day = start_date
        while day <= end_date:
            availability[day.isoformat()] = _status_for_date(
                villa.id, day, bookings_by_villa
            )
            day += timedelta(days=1)

        villas_payload.append({
            'id': villa.id,
            'name': villa.name,
            'short_name': _short_villa_name(villa.name),
            'bhk_type': _get_bhk_type(villa.name),
            'availability': availability,
        })

    return Response({
        'pricing': _compute_pricing(villas),
        'special_days': special_days_payload,
        'days': days_payload,
        'villas': villas_payload,
        'start': start_str,
        'end': end_str,
    })
