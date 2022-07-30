from django.conf import settings
from django.core.management.base import BaseCommand
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from corvee.src.corvee import Corvee


class Command(BaseCommand):
    help = "Synchronize members with central members database"

    def handle(self, *args, **options):
        client = BackendApplicationClient(client_id=settings.BACKEND_CLIENT_ID)
        session = OAuth2Session(client=client)
        token = session.fetch_token(settings.IDP_TOKEN_URL, client_secret=settings.BACKEND_CLIENT_SECRET)
        Corvee.update_members(token['access_token'])
