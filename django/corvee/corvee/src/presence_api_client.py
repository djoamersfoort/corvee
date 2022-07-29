from typing import List

from django.core.cache import cache
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from .models import Persoon


class PresenceApiClient:
    def __init__(self, presence_api_url, token_url, client_id, client_secret):
        self.api_url = presence_api_url
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.oauth = None

    def _authenticate(self):
        client = BackendApplicationClient(client_id=self.client_id)
        self.oauth = OAuth2Session(client=client)
        self.token = cache.get('presence_api_token')
        if not self.token:
            self.token = self.oauth.fetch_token(self.token_url, client_secret=self.client_secret)
            cache.set('presence_api_token', self.token, self.token['expires_in'])
        else:
            self.oauth.token = self.token

    def is_present(self, person: Persoon, day: str, pod: str) -> bool:
        if not self.oauth:
            self._authenticate()
        response = self.oauth.post(f'{self.api_url}/api/v2/is_present/{day}/{pod}/{person.idp_user_id}')
        if response.ok:
            return response.json()['present']
        return False

    def are_present(self, day: str, pod: str) -> List[str]:
        if not self.oauth:
            self._authenticate()
        response = self.oauth.post(f'{self.api_url}/api/v2/are_present/{day}/{pod}')
        if response.ok:
            return response.json()['members']
        return []
