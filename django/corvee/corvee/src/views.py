from requests_oauthlib import OAuth2Session
from django.views.generic.edit import View
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import logout, login as auth_login
from django.conf import settings
from django.views.generic.list import ListView
from django.shortcuts import reverse
from .models import Persoon, AuditLog
from .mixins import PermissionRequiredMixin
from .corvee import Corvee
from datetime import datetime, date, timedelta
import uuid


class Auditor:

    @staticmethod
    def audit(first_name, last_name, action, user):
        audit = AuditLog()
        audit.first_name = first_name
        audit.last_name = last_name
        audit.datetime = date.today()
        audit.action = action
        audit.performed_by = f"{user.first_name} {user.last_name}"
        audit.save()


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
            for required_role in settings.IDP_REQUIRED_ROLES:
                if required_role in user_profile['result']['accountType'].lower():
                    break
            else:
                return HttpResponseForbidden('Deze pagina is alleen toegankelijk voor bestuur en jeugdbestuur.')

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

        queryset = queryset.filter(selected=True)
        queryset = queryset.exclude(absent=date.today())
        queryset = queryset.order_by('latest')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['day'] = self.kwargs.get('day', 'friday')
        context['page'] = 'main'
        return context


class Leden(PermissionRequiredMixin, ListView):
    model = Persoon
    template_name = 'leden.html'

    def get_queryset(self):
        day = self.kwargs.get('day', 'friday')
        if day == 'friday':
            queryset = Persoon.objects.filter(day_friday=True)
        else:
            queryset = Persoon.objects.filter(day_saturday=True)

        queryset = queryset.order_by('latest')

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['day'] = self.kwargs.get('day', 'friday')
        context['page'] = 'leden'
        return context


class Acknowledge(PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        url = request.META.get('HTTP_REFERER', reverse('main'))

        persoon = Persoon.objects.get(pk=self.kwargs.get('pk'))
        persoon.latest = datetime.now()
        persoon.selected = False
        persoon.save()

        Auditor.audit(persoon.first_name, persoon.last_name, 'acknowledged', request.user)

        return HttpResponseRedirect(url)


class Insufficient(PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        url = request.META.get('HTTP_REFERER', reverse('main'))
        persoon = Persoon.objects.get(pk=self.kwargs.get('pk'))
        persoon.selected = False
        persoon.save()

        Auditor.audit(persoon.first_name, persoon.last_name, 'insufficient', request.user)

        return HttpResponseRedirect(url)


class Punishment(PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        url = request.META.get('HTTP_REFERER', reverse('main'))
        persoon = Persoon.objects.get(pk=self.kwargs.get('pk'))
        persoon.latest = date(1900, 1, 1)
        persoon.selected = False
        persoon.save()

        Auditor.audit(persoon.first_name, persoon.last_name, 'punishment', request.user)

        return HttpResponseRedirect(url)


class Absent(PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        url = request.META.get('HTTP_REFERER', reverse('main'))
        persoon = Persoon.objects.get(pk=self.kwargs.get('pk'))

        if request.user.first_name.lower() == persoon.first_name.lower() and request.user.last_name.lower() == persoon.last_name.lower():
            Auditor.audit(persoon.first_name, persoon.last_name, 'absent_self', request.user)
            return HttpResponseRedirect(url)

        persoon.selected = False
        persoon.absent = date.today()
        persoon.save()

        Auditor.audit(persoon.first_name, persoon.last_name, 'absent', request.user)

        day = self.kwargs.get('day', 'friday')

        if day == 'friday':
            queryset = Persoon.objects.filter(day_friday=True)
        else:
            queryset = Persoon.objects.filter(day_saturday=True)

        queryset = queryset.exclude(absent=date.today())
        queryset = queryset.exclude(latest__gt=date.today() - timedelta(days=settings.ABSOLVE_DAYS))
        queryset = queryset.exclude(selected=True)
        queryset = queryset.order_by('latest')

        if len(queryset) > 0:
            person = queryset[0]
            person.selected = True
            person.save()

        return HttpResponseRedirect(url)


class Renew(PermissionRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        url = request.META.get('HTTP_REFERER', reverse('main'))
        day = self.kwargs.get('day', 'friday')

        if day == 'friday':
            queryset = Persoon.objects.filter(day_friday=True)
        else:
            queryset = Persoon.objects.filter(day_saturday=True)

        queryset = queryset.exclude(absent=date.today())
        queryset = queryset.exclude(latest__gt=date.today() - timedelta(days=settings.ABSOLVE_DAYS))
        queryset = queryset.order_by('latest')
        queryset.update(selected=False)

        queryset = queryset[:3]
        for persoon in queryset:
            persoon.selected = True
            persoon.save()

        return HttpResponseRedirect(url)
