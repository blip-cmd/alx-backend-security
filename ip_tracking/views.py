from django.shortcuts import render

from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from ratelimit.decorators import ratelimit


@ratelimit(key="ip", rate="5/m", method="POST", block=True)  # 🚫 Anonymous users
@ratelimit(key="user_or_ip", rate="10/m", method="POST", block=True)  # ✅ Authenticated users
def login_view(request):
    """
    A sample login view protected by IP-based rate limiting.
    Anonymous: 5 requests/min
    Authenticated: 10 requests/min
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

