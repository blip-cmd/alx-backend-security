from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .tasks import detect_anomalies
from .models import RequestLog, SuspiciousIP
import json
# from django_ratelimit.decorators import ratelimit


# @ratelimit(key="ip", rate="5/m", method="POST", block=True)  # 🚫 Anonymous users
# @ratelimit(key="user_or_ip", rate="10/m", method="POST", block=True)  # ✅ Authenticated users
@api_view(['POST'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="User authentication endpoint",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        },
        required=['username', 'password']
    ),
    responses={
        200: openapi.Response(
            description='Login successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: 'Invalid credentials',
        405: 'Method not allowed'
    }
)
def login_view(request):
    """
    A sample login view protected by IP-based rate limiting.
    Anonymous: 5 requests/min
    Authenticated: 10 requests/min
    Note: Rate limiting temporarily disabled for development
    """
    if request.method == "POST":
        data = request.data if hasattr(request, 'data') else request.POST
        username = data.get("username")
        password = data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"status": "success", "message": "Logged in"})
        else:
            return Response({"status": "error", "message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"status": "error", "message": "POST required"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="Test background tasks functionality",
    responses={
        200: openapi.Response(
            description='Task executed successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'task_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'celery_eager': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                }
            )
        ),
        500: 'Task execution failed'
    }
)
@csrf_exempt
def test_tasks_view(request):
    """Test background tasks functionality"""
    try:
        # Run the anomaly detection task
        result = detect_anomalies.delay()
        
        # Since we're using CELERY_TASK_ALWAYS_EAGER=True, the task runs synchronously
        return Response({
            "status": "success",
            "message": "Background task executed successfully",
            "task_id": str(result.id) if hasattr(result, 'id') else "synchronous",
            "celery_eager": getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False)
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Task execution failed: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="Test email notification functionality",
    responses={
        200: openapi.Response(
            description='Email sent successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'email_backend': openapi.Schema(type=openapi.TYPE_STRING),
                    'email_host': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        500: 'Email sending failed'
    }
)
@csrf_exempt
def test_email_view(request):
    """Test email notification functionality"""
    try:
        subject = "ALX Backend Security - Test Email"
        message = "This is a test email from your deployed ALX Backend Security application."
        from_email = getattr(settings, 'EMAIL_HOST_USER', 'test@example.com')
        recipient_list = ['admin@example.com']  # You can change this to your email
        
        # Try to send email
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        
        return Response({
            "status": "success",
            "message": "Email sent successfully",
            "email_backend": settings.EMAIL_BACKEND,
            "email_host": getattr(settings, 'EMAIL_HOST', 'not configured')
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Email sending failed: {str(e)}",
            "email_backend": settings.EMAIL_BACKEND
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="View suspicious IPs detected by the system",
    responses={
        200: openapi.Response(
            description='Suspicious IPs retrieved successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'suspicious_ips': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'ip_address': openapi.Schema(type=openapi.TYPE_STRING),
                                'reason': openapi.Schema(type=openapi.TYPE_STRING),
                                'detected_at': openapi.Schema(type=openapi.TYPE_STRING),
                                'is_blocked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            }
                        )
                    ),
                }
            )
        ),
        500: 'Failed to fetch suspicious IPs'
    }
)
def suspicious_ips_view(request):
    """View suspicious IPs detected by the system"""
    try:
        suspicious_ips = SuspiciousIP.objects.all().order_by('-detected_at')[:20]
        data = []
        for ip in suspicious_ips:
            data.append({
                "ip_address": ip.ip_address,
                "reason": ip.reason,
                "detected_at": ip.detected_at.isoformat(),
                "is_blocked": ip.is_blocked
            })
        
        return Response({
            "status": "success",
            "count": len(data),
            "suspicious_ips": data
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Failed to fetch suspicious IPs: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
@swagger_auto_schema(
    operation_description="View recent request logs",
    responses={
        200: openapi.Response(
            description='Request logs retrieved successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'request_logs': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'ip_address': openapi.Schema(type=openapi.TYPE_STRING),
                                'path': openapi.Schema(type=openapi.TYPE_STRING),
                                'method': openapi.Schema(type=openapi.TYPE_STRING),
                                'user_agent': openapi.Schema(type=openapi.TYPE_STRING),
                                'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                                'city': openapi.Schema(type=openapi.TYPE_STRING),
                                'country': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    ),
                }
            )
        ),
        500: 'Failed to fetch request logs'
    }
)
def request_logs_view(request):
    """View recent request logs"""
    try:
        logs = RequestLog.objects.all().order_by('-timestamp')[:50]
        data = []
        for log in logs:
            data.append({
                "ip_address": log.ip_address,
                "path": log.path,
                "method": log.method,
                "user_agent": log.user_agent,
                "timestamp": log.timestamp.isoformat(),
                "city": getattr(log, 'city', 'Unknown'),
                "country": getattr(log, 'country', 'Unknown')
            })
        
        return Response({
            "status": "success",
            "count": len(data),
            "request_logs": data
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Failed to fetch request logs: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

