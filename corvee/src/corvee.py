from datetime import date, timedelta

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from corvee.src.models import Persoon, LastSync
from corvee.src.presence_api_client import PresenceApiClient


class Corvee:
    type_filter = {'member', 'senior', 'strippenkaart'}
    
    @staticmethod
    def is_sync_needed():
        try:
            last_sync = LastSync.objects.get()
        except LastSync.DoesNotExist:
            last_sync = LastSync()

        sync_needed = last_sync.last_sync_date != date.today()
        last_sync.last_sync_date = date.today()
        last_sync.save()
        return sync_needed

    @staticmethod
    def update_members(access_token):
        if not Corvee.is_sync_needed():
            return

        response = requests.get(settings.LEDEN_ADMIN_API_URL,
                                headers={'Authorization': f'Bearer {access_token}'}, timeout=60)
        if not response.ok:
            print(f"Error getting members: {response.status_code}, {response.content}")

        Persoon.objects.all().update(marked_for_deletion=True)

        members = response.json()
        for member in members:
            type_set = set(member['types'])
            if not Corvee.type_filter.intersection(type_set):
                continue

            try:
                persoon = Persoon.objects.get(id=member['id'])
            except Persoon.DoesNotExist:
                persoon = Persoon()
            persoon.id = member['id']
            persoon.idp_user_id = member['user_id']
            persoon.first_name = member['first_name']
            persoon.last_name = member['last_name']
            persoon.picture = member['photo']
            # Disable deletion mark
            persoon.marked_for_deletion = False
            persoon.save()

        # Delete members not updated / present in member administration
        Persoon.objects.filter(marked_for_deletion=True).delete()

    @staticmethod
    def _get_pod():
        pod = 'm'
        hour = timezone.now().hour
        if hour >= 18:
            pod = 'e'
        elif hour >= 13:
            pod = 'a'
        return pod

    @staticmethod
    def renew_list(requery_present_members=True):
        weekday = timezone.now().weekday()
        day = 'fri' if weekday == 4 else 'sat'
        if weekday not in [4, 5]:
            return
        pod = Corvee._get_pod()
        if requery_present_members:
            # Get list of present members from 'Aanmelden' API
            presence = PresenceApiClient(client_id=settings.BACKEND_CLIENT_ID,
                                         client_secret=settings.BACKEND_CLIENT_SECRET,
                                         token_url=settings.IDP_TOKEN_URL, presence_api_url=settings.PRESENCE_API_URL)
            present_members = presence.are_present(day, pod)
            Persoon.objects.update(selected=False, absent=True)
            Persoon.objects.filter(idp_user_id__in=present_members).update(absent=False)
        else:
            # Reset 'selected' flag for everyone
            Persoon.objects.update(selected=False)

        queryset = Persoon.objects.all().exclude(absent=True)
        queryset = queryset.exclude(latest__gt=timezone.now() - timedelta(days=settings.ABSOLVE_DAYS))
        queryset = queryset.order_by('latest')

        # Select oldest 3 members based on 'latest' date
        with transaction.atomic():
            selected = queryset[:3]
            for persoon in selected:
                persoon.selected = True
                persoon.save()
