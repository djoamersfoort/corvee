from django.views import View
from django.http.response import JsonResponse
from .models import Persoon


class SelectedV1(View):
    def get(self, request, *args, **kwargs):
        selected = Persoon.objects.filter(selected=True)
        names = [person.first_name for person in selected]
        return JsonResponse({"selected": names})
