from requests_oauthlib import OAuth2Session
from django.views.generic.edit import View
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import logout, login as auth_login
from django.conf import settings
from django.views.generic.list import ListView
from .models import Persoon
from .mixins import PermissionRequiredMixin
from .corvee import Corvee
import uuid


class LoginView(View):
    def get(self, request, *args, **kwargs):
        oauth = OAuth2Session(client_id=settings.IDP_CLIENT_ID,
                              redirect_uri=settings.IDP_REDIRECT_URL,
                              scope=['user/basic', 'user/account-type', 'user/names', 'user/email'])
        auth_url, state = oauth.authorization_url(settings.IDP_AUTHORIZE_URL)
        return HttpResponseRedirect(auth_url)


class LoginResponseView(View):
    def get(self, request, *args, **kwargs):
        oauth = OAuth2Session(client_id=settings.IDP_CLIENT_ID,
                              redirect_uri=settings.IDP_REDIRECT_URL)
        full_response_url = request.build_absolute_uri()
        full_response_url = full_response_url.replace('http:', 'https:')
        try:
            access_token = oauth.fetch_token(settings.IDP_TOKEN_URL,
                                             authorization_response=full_response_url,
                                             client_secret=settings.IDP_CLIENT_SECRET)
        except Exception as e:
            # Something went wrong getting the token
            return HttpResponseForbidden('Geen toegang: {0}'.format(e))

        if 'access_token' in access_token and access_token['access_token'] != '':
            user_profile = oauth.get(settings.IDP_API_URL).json()
            username = "idp-{0}".format(user_profile['result']['id'])
            if settings.IDP_REQUIRED_ROLE not in user_profile['result']['accountType'].lower():
                return HttpResponseForbidden('Verplichte rol niet toegekend')

            try:
                found_user = User.objects.get(username=username)
            except User.DoesNotExist:
                found_user = User()
                found_user.username = username
                found_user.password = uuid.uuid4()
                found_user.email = user_profile['result']['email']
                found_user.first_name = user_profile['result']['firstName']
                found_user.last_name = user_profile['result']['lastName']
                found_user.is_superuser = True
                found_user.save()

            auth_login(request, found_user)

            # Sync the database with member-admin
            Corvee.update_members(access_token['access_token'])

            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        else:
            return HttpResponseForbidden('IDP Login mislukt')


class LogoffView(PermissionRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponse(content='Uitgelogd')


class Main(PermissionRequiredMixin, ListView):
    model = Persoon
    template_name = 'index.html'

    def get_queryset(self):
        day = self.kwargs.get('day', 'friday')
        if day == 'friday':
            queryset = Persoon.objects.filter(day_friday=True)
        else:
            queryset = Persoon.objects.filter(day_saturday=True)

        queryset = queryset.order_by('-latest')
        return queryset
