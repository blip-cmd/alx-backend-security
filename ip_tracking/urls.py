from django.urls import path
from . import views

app_name = 'ip_tracking'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('test-tasks/', views.test_tasks_view, name='test-tasks'),
    path('test-email/', views.test_email_view, name='test-email'),
    path('suspicious-ips/', views.suspicious_ips_view, name='suspicious-ips'),
    path('request-logs/', views.request_logs_view, name='request-logs'),
]
