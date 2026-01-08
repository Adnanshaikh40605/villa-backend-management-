from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .serializers import UserSerializer, LoginSerializer

# Import jwt only when needed (token validation endpoint)
# PyJWT should be installed as a dependency of djangorestframework-simplejwt
try:
    import jwt
except ImportError:
    jwt = None  # Will be handled in token_validate_view


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint - returns JWT tokens and user data
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    user = authenticate(request, username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'Account is inactive'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate tokens
    try:
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
    except Exception as e:
        # Log the error for debugging
        import traceback
        error_detail = str(e)
        traceback.print_exc()
        
        return Response(
            {
                'error': 'Failed to generate authentication tokens',
                'detail': error_detail if settings.DEBUG else 'Internal server error'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """
    Get current user profile
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def token_validate_view(request):
    """
    Token validation and debugging endpoint
    
    GET: Returns information about the current authenticated token
    POST: Validates a token passed in the request body
    
    This endpoint helps debug token expiration issues by providing:
    - Token expiration time
    - Issued at time
    - Time remaining until expiration
    - Token type (access/refresh)
    - User information
    - Blacklist status
    """
    # Check if jwt is available
    if jwt is None:
        return Response(
            {'error': 'PyJWT is not installed. Please install it: pip install PyJWT==2.8.0'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    try:
        # For POST requests, token can be passed in body
        if request.method == 'POST':
            token_string = request.data.get('token')
            if not token_string:
                return Response(
                    {'error': 'Token is required in request body'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # For GET requests, extract from Authorization header
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return Response(
                    {'error': 'Authorization header with Bearer token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token_string = auth_header.split(' ')[1]
        
        # Decode token without verification first to check expiration
        try:
            decoded_token = jwt.decode(
                token_string,
                options={"verify_signature": False},
                algorithms=['HS256']
            )
        except jwt.DecodeError:
            return Response(
                {'error': 'Invalid token format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract token information
        exp = decoded_token.get('exp')
        iat = decoded_token.get('iat')
        token_type = decoded_token.get('token_type', 'access')
        user_id = decoded_token.get('user_id')
        jti = decoded_token.get('jti')  # JWT ID for blacklist checking
        
        # Calculate time remaining
        if exp:
            now = timezone.now().timestamp()
            time_remaining = exp - now
            is_expired = time_remaining <= 0
            
            # Convert to readable format
            from datetime import datetime
            exp_datetime = datetime.fromtimestamp(exp)
            iat_datetime = datetime.fromtimestamp(iat) if iat else None
            
            # Check if token is blacklisted (import here to avoid breaking login if migrations not run)
            is_blacklisted = False
            if jti:
                try:
                    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
                    outstanding_token = OutstandingToken.objects.filter(jti=jti).first()
                    if outstanding_token:
                        is_blacklisted = BlacklistedToken.objects.filter(token=outstanding_token).exists()
                except Exception:
                    pass  # Ignore errors when checking blacklist (migrations might not be run)
            
            # Verify token signature and get user info if valid
            user_info = None
            is_signature_valid = False
            try:
                # Verify token signature
                secret_key = settings.SECRET_KEY
                jwt.decode(token_string, secret_key, algorithms=['HS256'])
                is_signature_valid = True
                
                # Get user info if valid
                if user_id:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    try:
                        user = User.objects.get(id=user_id)
                        user_info = {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                        }
                    except User.DoesNotExist:
                        pass
            except jwt.InvalidTokenError:
                pass  # Signature invalid, but we still return decoded info
        
            response_data = {
                'token_type': token_type,
                'exp': exp,
                'exp_datetime': exp_datetime.isoformat() if exp_datetime else None,
                'iat': iat,
                'iat_datetime': iat_datetime.isoformat() if iat_datetime else None,
                'time_remaining_seconds': int(time_remaining) if time_remaining > 0 else 0,
                'time_remaining_readable': _format_timedelta(timedelta(seconds=int(time_remaining))) if time_remaining > 0 else 'Expired',
                'is_expired': is_expired,
                'is_signature_valid': is_signature_valid,
                'is_blacklisted': is_blacklisted,
                'user_id': user_id,
                'user_info': user_info,
                'jti': jti,
                'server_time': timezone.now().isoformat(),
            }
            
            if is_expired:
                return Response(
                    response_data,
                    status=status.HTTP_401_UNAUTHORIZED
                )
            else:
                return Response(response_data)
        else:
            return Response(
                {'error': 'Token does not contain expiration claim (exp)'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': f'Error validating token: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _format_timedelta(td):
    """Format timedelta to human-readable string"""
    total_seconds = int(td.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f'{days} day{"s" if days != 1 else ""}')
    if hours > 0:
        parts.append(f'{hours} hour{"s" if hours != 1 else ""}')
    if minutes > 0:
        parts.append(f'{minutes} minute{"s" if minutes != 1 else ""}')
    if seconds > 0 or not parts:
        parts.append(f'{seconds} second{"s" if seconds != 1 else ""}')
    
    return ', '.join(parts)

