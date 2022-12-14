from django.conf import settings
from django.http.request import HttpRequest
from rest_framework.authtoken.models import Token


def settings_context(request):
    return {'settings': settings}


def token_context(request: HttpRequest):
    if request.user.is_authenticated:
        return {'token': Token.objects.filter(user=request.user).first()}
    return {}
