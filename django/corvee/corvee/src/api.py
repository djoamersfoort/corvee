from django.http.response import JsonResponse
from django.views import View

from .models import Persoon


class SelectedV1(View):
    def get(self, request, *args, **kwargs):
        selected = Persoon.objects.filter(selected=True)
        present = Persoon.objects.filter(absent=False)
        names = [person.first_name for person in selected]
        present_names = [person.first_name for person in present]
        return JsonResponse({"selected": names, "present": present_names})
