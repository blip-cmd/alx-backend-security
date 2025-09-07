"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import redirect
from ip_tracking.views import login_view

# Swagger imports
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'alx-backend-security'})

def api_root(request):
    """API root endpoint with available endpoints"""
    return JsonResponse({
        'message': 'ALX Backend Security API',
        'version': 'v1',
        'endpoints': {
            'health': '/health/',
            'swagger_docs': '/swagger/',
            'redoc_docs': '/redoc/',
            'admin': '/admin/',
            'api': '/api/v1/',
            'login': '/login/',
        },
        'api_endpoints': {
            'login': '/api/v1/login/',
            'test_tasks': '/api/v1/test-tasks/',
            'test_email': '/api/v1/test-email/',
            'suspicious_ips': '/api/v1/suspicious-ips/',
            'request_logs': '/api/v1/request-logs/',
        }
    })

def redirect_to_swagger(request):
    """Redirect root to swagger documentation"""
    return redirect('/swagger/')

schema_view = get_schema_view(
    openapi.Info(
        title="ALX Backend Security API",
        default_version='v1',
        description="""
        # ALX Backend Security API Documentation
        
        This API provides endpoints for IP tracking, security monitoring, and user authentication.
        
        ## Features
        - IP tracking and geolocation
        - Suspicious activity detection
        - Request logging and monitoring
        - Background task processing
        - Email notifications
        
        ## Available Endpoints
        - `/health/` - Health check endpoint
        - `/api/v1/login/` - User authentication
        - `/api/v1/suspicious-ips/` - View suspicious IP addresses
        - `/api/v1/request-logs/` - View request logs
        - `/api/v1/test-tasks/` - Test background tasks
        - `/api/v1/test-email/` - Test email functionality
        """,
        terms_of_service="https://example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root endpoint - redirects to swagger docs
    path('', redirect_to_swagger, name='root'),
    
    # API info endpoint
    path('api/', api_root, name='api-root'),
    
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('login/', login_view, name='login'),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API endpoints
    path('api/v1/', include('ip_tracking.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
