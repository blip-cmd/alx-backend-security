from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@login_required
def login_view(request):
    return HttpResponse('Authenticated login attempt')

@csrf_exempt
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def anonymous_login_view(request):
    return HttpResponse('Anonymous login attempt')
