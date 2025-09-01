import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP
from django.core.cache import cache
from ipgeolocation import IpGeolocationAPI
from django.conf import settings

class IPTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)
        path = request.path
        # Blocked IP check
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden('Your IP is blacklisted.')
        # Geolocation (cached for 24h)
        geo = cache.get(f'geo_{ip}')
        if not geo:
            api_key = getattr(settings, 'IPGEOLOCATION_API_KEY', None)
            if api_key:
                geo_api = IpGeolocationAPI(api_key)
                try:
                    geo_data = geo_api.get_geolocation(ip_address=ip)
                    country = geo_data.get('country_name', '')
                    city = geo_data.get('city', '')
                except Exception:
                    country = ''
                    city = ''
            else:
                country = ''
                city = ''
            geo = {'country': country, 'city': city}
            cache.set(f'geo_{ip}', geo, 60*60*24)
        # Log request
        RequestLog.objects.create(ip_address=ip, path=path, country=geo['country'], city=geo['city'])

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
