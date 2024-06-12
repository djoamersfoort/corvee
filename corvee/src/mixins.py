import jwt
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from django.views import View

from corvee.src.utils import get_access_token, get_openid_configuration, get_jwks_client


class PermissionRequiredMixin(UserPassesTestMixin):
    required_permission = 'corvee.view_persoon'

    def check_user(self, user):
        if user.is_authenticated and user.has_perm(self.required_permission) and user.is_active:
            return True
        return False

    def test_func(self):
        return self.check_user(self.request.user)


class TokenRequiredMixin(View):
    def dispatch(self, request, *args, **kwargs):
        given_token = request.headers.get("Authorization", "").lower()
        correct_token = f"Bearer {settings.API_TOKEN}".lower()

        if given_token == correct_token:
            return super(TokenRequiredMixin, self).dispatch(request, *args, **kwargs)
            
        return HttpResponse("401 JOCH!", status=401, content_type="text/plain")


class AuthenticatedMixin:
    def dispatch(self, request, *args, **kwargs):
        token = get_access_token(request)
        if not token:
            return HttpResponseForbidden()

        openid_configuration = get_openid_configuration()
        jwks_client = get_jwks_client()

        signing_key = jwks_client.get_signing_key_from_jwt(token)
        decoded_jwt = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=openid_configuration['id_token_signing_alg_values_supported'],
            options={'verify_aud': False}
        )
        if 'corvee' not in decoded_jwt:
            return HttpResponseForbidden()

        username = f"idp-{decoded_jwt['sub']}"
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username)
            user.set_unusable_password()
            user.first_name = decoded_jwt['given_name']
            user.last_name = decoded_jwt['family_name']
            user.is_superuser = True
            user.save()

        if not user.is_staff:
            for required_role in settings.IDP_REQUIRED_ROLES:
                if required_role in decoded_jwt['account_type'].lower():
                    break
            else:
                return HttpResponseForbidden()

        request.user = user

        return super().dispatch(request, *args, **kwargs)
