from django.http.response import JsonResponse
from django.utils import timezone
from django.views import View

from corvee.src.corvee import Corvee
from corvee.src.mixins import TokenRequiredMixin
from corvee.src.models import Persoon
from corvee.src.mixins import AuthenticatedMixin
from corvee.src.utils import acknowledge, insufficient, punishment, absent


class SelectedV1(TokenRequiredMixin):
    def get(self, request, *args, **kwargs):
        selected = Persoon.objects.filter(selected=True)
        present = Persoon.objects.filter(absent=False)
        names = [person.short_name for person in selected]
        present_names = [person.short_name for person in present]
        return JsonResponse({"selected": names, "present": present_names})


class StatusV1(AuthenticatedMixin, View):
    def get(self, request, *args, **kwargs):
        weekday = timezone.now().weekday()
        day = "fri" if weekday == 4 else "sat"
        pod = Corvee.get_pod()
        if weekday not in [4, 5]:
            return JsonResponse({"ok": False, "error": "Vandaag is er geen corvee"})

        return JsonResponse({
            "current": list(Persoon.objects.filter(selected=True).order_by('latest').values()),
            "day": day,
            "pod": pod
        })


class RenewV1(AuthenticatedMixin, View):
    def get(self, request, *args, **kwargs):
        Corvee.renew_list()
        return JsonResponse({"ok": True})


class AcknowledgeV1(AuthenticatedMixin, View):
    def get(self, request, *args, **kwargs):
        acknowledge(request, self.kwargs.get('pk'))

        return JsonResponse({"ok": True})


class InsufficientV1(AuthenticatedMixin, View):
    def get(self, request, *args, **kwargs):
        insufficient(request, self.kwargs.get('pk'))

        return JsonResponse({"ok": True})


class PunishmentV1(AuthenticatedMixin, View):
    def get(self, request, *args, **kwargs):
        punishment(request, self.kwargs.get('pk'))

        return JsonResponse({"ok": True})


class AbsentV1(AuthenticatedMixin, View):
    def get(self, request, *args, **kwargs):
        absent(request, self.kwargs.get('pk'))

        return JsonResponse({"ok": True})
