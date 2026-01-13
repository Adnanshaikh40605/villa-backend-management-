from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from .models import Villa, GlobalSpecialDay
from .serializers import VillaSerializer, VillaListSerializer, GlobalSpecialDaySerializer
from bookings.models import Booking


class GlobalSpecialDayViewSet(viewsets.ModelViewSet):
    queryset = GlobalSpecialDay.objects.all()
    serializer_class = GlobalSpecialDaySerializer


class VillaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Villa CRUD operations
    """
    queryset = Villa.objects.all()
    serializer_class = VillaSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VillaListSerializer
        return VillaSerializer
    
    def get_queryset(self):
        queryset = Villa.objects.all()
        status_filter = self.request.query_params.get('status', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset



    def perform_create(self, serializer):
        new_order = serializer.validated_data.get('order', 0)
        if new_order and new_order > 0:
            from django.db.models import F
            Villa.objects.filter(order__gte=new_order).update(order=F('order') + 1)
        serializer.save()

    def perform_update(self, serializer):
        new_order = serializer.validated_data.get('order')
        instance = serializer.instance
        old_order = instance.order

        # Only proceed if order is provided, non-zero, and actually changing
        if new_order is not None and new_order > 0 and new_order != old_order:
            from django.db.models import F
            
            if old_order == 0:
                # Case 1: Was unassigned (0), now assigned (X).
                # Treat like a new insertion: Shift everything >= X down by 1.
                Villa.objects.filter(order__gte=new_order).update(order=F('order') + 1)
                
            elif new_order < old_order:
                # Case 2: Moving UP (e.g., 4 -> 2)
                # We want to place item at 2. 
                # Items currently at 2, 3 must shift DOWN (+1) to become 3, 4.
                # Range to shift: [new_order, old_order - 1]
                Villa.objects.filter(
                    order__gte=new_order, 
                    order__lt=old_order
                ).update(order=F('order') + 1)
                
            elif new_order > old_order:
                # Case 3: Moving DOWN (e.g., 2 -> 4)
                # We want to place item at 4.
                # Items currently at 3, 4 must shift UP (-1) to become 2, 3.
                # Range to shift: [old_order + 1, new_order]
                Villa.objects.filter(
                    order__gt=old_order, 
                    order__lte=new_order
                ).update(order=F('order') - 1)
            
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Check villa availability for given date range
        GET /api/v1/villas/{id}/availability/?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD
        """
        villa = self.get_object()
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        if not check_in or not check_out:
            return Response(
                {'error': 'check_in and check_out parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for overlapping bookings
        conflicting_bookings = Booking.objects.filter(
            villa=villa,
            check_in__lt=check_out,
            check_out__gt=check_in
        ).values('id', 'client_name', 'check_in', 'check_out')
        
        available = not conflicting_bookings.exists()
        
        # Determine conflicts (fetch only if needed)
        conflicting_data = list(conflicting_bookings) if not available else []
        
        return Response({
            'available': available,
            'conflicting_bookings': conflicting_data
        })
