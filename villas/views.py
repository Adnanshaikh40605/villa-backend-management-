from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Villa
from .serializers import VillaSerializer, VillaListSerializer
from bookings.models import Booking


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
