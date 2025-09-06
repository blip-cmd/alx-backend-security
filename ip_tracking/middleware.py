from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.core.cache import cache
from ipgeolocation import IpGeoLocation
from .models import RequestLog, BlockedIP


class IPLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that:
    - Blocks blacklisted IPs
    - Logs request details
    - Adds geolocation (country, city) with caching
    """

    def get_client_ip(self, request):
        """Retrieve client IP address (handles proxies)."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def get_geolocation(self, ip):
        """Fetch geolocation data (with 24h cache)."""
        cache_key = f"geo_{ip}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            geo = IpGeoLocation(ip)
            data = {
                "country": geo.country_name,
                "city": geo.city,
            }
        except Exception:
            data = {"country": None, "city": None}

        # Cache for 24 hours
        cache.set(cache_key, data, timeout=60 * 60 * 24)
        return data

    def process_request(self, request):
        ip = self.get_client_ip(request)

        # 🚫 Block if IP is blacklisted
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # 🌍 Geolocation lookup
        geo_data = self.get_geolocation(ip)

        # ✅ Log request
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            timestamp=timezone.now(),
            country=geo_data.get("country"),
            city=geo_data.get("city"),
        )
