from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .tasks import detect_anomalies
from .models import RequestLog, SuspiciousIP
import json
# from django_ratelimit.decorators import ratelimit


# @ratelimit(key="ip", rate="5/m", method="POST", block=True)  # 🚫 Anonymous users
# @ratelimit(key="user_or_ip", rate="10/m", method="POST", block=True)  # ✅ Authenticated users
def login_view(request):
    """
    A sample login view protected by IP-based rate limiting.
    Anonymous: 5 requests/min
    Authenticated: 10 requests/min
    Note: Rate limiting temporarily disabled for development
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"status": "success", "message": "Logged in"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=400)

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)


@csrf_exempt
def test_tasks_view(request):
    """Test background tasks functionality"""
    try:
        # Run the anomaly detection task
        result = detect_anomalies.delay()
        
        # Since we're using CELERY_TASK_ALWAYS_EAGER=True, the task runs synchronously
        return JsonResponse({
            "status": "success",
            "message": "Background task executed successfully",
            "task_id": str(result.id) if hasattr(result, 'id') else "synchronous",
            "celery_eager": getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False)
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Task execution failed: {str(e)}"
        }, status=500)


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
        
        return JsonResponse({
            "status": "success",
            "message": "Email sent successfully",
            "email_backend": settings.EMAIL_BACKEND,
            "email_host": getattr(settings, 'EMAIL_HOST', 'not configured')
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Email sending failed: {str(e)}",
            "email_backend": settings.EMAIL_BACKEND
        }, status=500)


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
        
        return JsonResponse({
            "status": "success",
            "count": len(data),
            "suspicious_ips": data
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Failed to fetch suspicious IPs: {str(e)}"
        }, status=500)


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
        
        return JsonResponse({
            "status": "success",
            "count": len(data),
            "request_logs": data
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Failed to fetch request logs: {str(e)}"
        }, status=500)

