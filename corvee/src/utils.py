from datetime import datetime
from functools import lru_cache

import requests
from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone
from jwt import PyJWKClient

from corvee.src.corvee import Corvee
from corvee.src.models import AuditLog, Persoon


class Auditor:

    @staticmethod
    def audit(first_name, last_name, action, user):
        audit = AuditLog()
        audit.first_name = first_name
        audit.last_name = last_name
        audit.datetime = timezone.now().date()
        audit.action = action
        audit.performed_by = f"{user.first_name} {user.last_name}"
        audit.save()


@lru_cache()
def get_openid_configuration():
    return requests.get(settings.OPENID_CONFIGURATION, timeout=10).json()


@lru_cache()
def get_jwks_client():
    return PyJWKClient(uri=get_openid_configuration()['jwks_uri'])


def get_access_token(request) -> (str, None):
    token = request.GET.get('access_token', '').strip()
    if token == "":
        parts = request.headers.get('authorization', '').split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]
    if token == "":
        return None
    return token


def acknowledge(request: HttpRequest, pk: str):
    persoon = Persoon.objects.get(pk=pk)
    persoon.latest = timezone.now()
    persoon.selected = False
    persoon.save()

    Auditor.audit(persoon.first_name, persoon.last_name, 'acknowledged', request.user)


def insufficient(request: HttpRequest, pk: str):
    persoon = Persoon.objects.get(pk=pk)
    persoon.selected = False
    persoon.save()

    Auditor.audit(persoon.first_name, persoon.last_name, 'insufficient', request.user)


def absent(request: HttpRequest, pk: str):
    persoon = Persoon.objects.get(pk=pk)
    persoon.selected = False
    persoon.absent = True
    persoon.save()

    Auditor.audit(persoon.first_name, persoon.last_name, 'absent', request.user)

    Corvee.renew_list(requery_present_members=False)


def punishment(request: HttpRequest, pk: str):
    persoon = Persoon.objects.get(pk=pk)
    persoon.latest = timezone.make_aware(datetime(1900, 1, 1, 0, 0, 0))
    persoon.selected = False
    persoon.save()

    Auditor.audit(persoon.first_name, persoon.last_name, 'punishment', request.user)
