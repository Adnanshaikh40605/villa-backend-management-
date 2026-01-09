from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def health_check(request):
    """
    Health check endpoint for Railway and monitoring services.
    Returns a simple JSON response indicating the API is running.
    No authentication required.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'Villa Management API',
        'version': '1.0.0'
    })


def home_view(request):
    """Simple home page view"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Villa Management System - API</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 60px 40px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                text-align: center;
                max-width: 600px;
                width: 100%;
            }
            h1 {
                color: #333;
                font-size: 2.5rem;
                margin-bottom: 20px;
                font-weight: 700;
            }
            p {
                color: #666;
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 30px;
            }
            .links {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }
            a {
                display: inline-block;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 10px;
                font-weight: 600;
                transition: all 0.3s ease;
                font-size: 1rem;
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }
            .btn-secondary {
                background: #f0f0f0;
                color: #333;
            }
            .btn-secondary:hover {
                background: #e0e0e0;
                transform: translateY(-2px);
            }
            .icon {
                font-size: 4rem;
                margin-bottom: 20px;
            }
            .info {
                margin-top: 40px;
                padding-top: 30px;
                border-top: 2px solid #f0f0f0;
            }
            .info-item {
                margin: 10px 0;
                color: #888;
                font-size: 0.9rem;
            }
            .info-item strong {
                color: #667eea;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">🏖️</div>
            <h1>Welcome to Villa Management System</h1>
            <p>This is the backend API server. To manage your villa bookings and reservations, please visit the admin dashboard.</p>
            
            <div class="links">
                <a href="https://www.vacationbna.ai/" class="btn-primary">Go to Dashboard</a>
                <a href="/admin/" class="btn-secondary">Admin Panel</a>
                <a href="/api/docs/" class="btn-secondary">API Docs</a>
            </div>
            
            <div class="info">
                <div class="info-item"><strong>Frontend:</strong> https://www.vacationbna.ai/</div>
                <div class="info-item"><strong>API Documentation:</strong> /api/docs/</div>
                <div class="info-item"><strong>Admin Panel:</strong> /admin/</div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
