from django.http.response import JsonResponse

from corvee.src.models import Persoon
from corvee.src.mixins import TokenRequiredMixin


class SelectedV1(TokenRequiredMixin):
    def get(self, request, *args, **kwargs):
        selected = Persoon.objects.filter(selected=True)
        present = Persoon.objects.filter(absent=False)
        names = [person.short_name for person in selected]
        present_names = [person.short_name for person in present]
        return JsonResponse({"selected": names, "present": present_names})
