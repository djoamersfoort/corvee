from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.conf import settings
from django.views import View


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
