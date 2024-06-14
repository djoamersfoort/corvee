import uuid

from django.conf import settings
from django.contrib.auth import logout, login as auth_login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import reverse
from django.views.generic.edit import View
from django.views.generic.list import ListView
from requests_oauthlib import OAuth2Session

from corvee.src.corvee import Corvee
from corvee.src.mixins import PermissionRequiredMixin
from corvee.src.models import Persoon
from corvee.src.utils import acknowledge, insufficient, punishment, absent


class LoginView(View):
    def get(self, request, *args, **kwargs):
        oauth = OAuth2Session(client_id=settings.IDP_CLIENT_ID,
                              redirect_uri=settings.IDP_REDIRECT_URL,
                              scope=settings.IDP_SCOPES)
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
        except Exception:
            # Something went wrong getting the token
            return HttpResponseForbidden()

        if 'access_token' not in access_token or access_token['access_token'] == '':
            return HttpResponseForbidden('IDP Login mislukt')

        user_profile = oauth.get(settings.IDP_API_URL).json()
        username = "idp-{0}".format(user_profile['id'])

        try:
            found_user = User.objects.get(username=username)
        except User.DoesNotExist:
            found_user = User()
            found_user.username = username
            found_user.password = uuid.uuid4()
            found_user.first_name = user_profile['firstName']
            found_user.last_name = user_profile['lastName']
            found_user.is_superuser = True
            found_user.save()

        if not found_user.is_staff:
            for required_role in settings.IDP_REQUIRED_ROLES:
                if required_role in user_profile['accountType'].lower():
                    break
            else:
                roles = ','.join(settings.IDP_REQUIRED_ROLES)
                return HttpResponseForbidden(f'Deze pagina is alleen toegankelijk voor de volgende rollen: {roles}.')

        auth_login(request, found_user)

        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


class LogoffView(PermissionRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponse(content='Uitgelogd')


class Main(PermissionRequiredMixin, ListView):
    model = Persoon
    template_name = 'index.html'

    def get_queryset(self):
        return Persoon.objects.filter(selected=True).order_by('latest')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['page'] = 'main'
        return context


class Leden(PermissionRequiredMixin, ListView):
    model = Persoon
    template_name = 'leden.html'

    def get_queryset(self):
        return Persoon.objects.all().order_by('latest')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['page'] = 'leden'
        return context


class Acknowledge(PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        acknowledge(request, self.kwargs.get('pk'))

        return HttpResponseRedirect(reverse('main'))


class Insufficient(PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        insufficient(request, self.kwargs.get('pk'))

        return HttpResponseRedirect(reverse('main'))


class Punishment(PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        punishment(request, self.kwargs.get('pk'))

        return HttpResponseRedirect(reverse('main'))


class Absent(PermissionRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        absent(request, self.kwargs.get('pk'))

        return HttpResponseRedirect(reverse('main'))


class Renew(PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        Corvee.renew_list()
        return HttpResponseRedirect(reverse('main'))
