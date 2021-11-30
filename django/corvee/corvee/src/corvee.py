from .models import Persoon, LastSync
from django.conf import settings
from datetime import date, timedelta
from .presence_api_client import PresenceApiClient
import datetime
import requests


class Corvee:

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
                                headers={'Authorization': 'Bearer {0}'.format(access_token)})
        if response.ok:
            Persoon.objects.all().update(marked_for_deletion=True, day_friday=False, day_saturday=False)

            members = response.json()
            for dag in members:
                for member in members[dag]:
                    if 'member' not in member['types'] and 'strippenkaart' not in member['types']:
                        continue

                    try:
                        persoon = Persoon.objects.get(id=member['id'])
                    except Persoon.DoesNotExist:
                        persoon = Persoon()
                    persoon.id = member['id']
                    persoon.idp_user_id = member['user_id']
                    persoon.first_name = member['first_name']
                    persoon.last_name = member['last_name']
                    if dag == 'vrijdag':
                        persoon.day_friday = True
                    if dag == 'zaterdag':
                        persoon.day_saturday = True
                    persoon.picture = member['photo']
                    # Disable deletion mark
                    persoon.marked_for_deletion = False
                    persoon.save()

            # Delete members not updated / present in member administration
            Persoon.objects.filter(marked_for_deletion=True).delete()
        else:
            print("Error getting members: {0}".format(response.content))

    @staticmethod
    def _get_pod():
        pod = 'm'
        hour = datetime.datetime.now().hour
        if hour >= 13:
            pod = 'a'
        elif hour >= 18:
            pod = 'e'
        return pod

    @staticmethod
    def renew_list():
        weekday = date.today().weekday()
        day = 'fri' if weekday == 4 else 'sat'
        if weekday not in [4, 5]:
            return
        pod = Corvee._get_pod()
        presence = PresenceApiClient(client_id=settings.PRESENCE_CLIENT_ID,
                                     client_secret=settings.PRESENCE_CLIENT_SECRET,
                                     token_url=settings.IDP_TOKEN_URL, presence_api_url=settings.PRESENCE_API_URL)
        queryset = Persoon.objects.all()
        for persoon in queryset:
            persoon.selected = False
            if not presence.is_present(persoon, day, pod):
                persoon.absent = date.today()
            persoon.save()

        queryset = queryset.exclude(absent=date.today())
        queryset = queryset.exclude(latest__gt=date.today() - timedelta(days=settings.ABSOLVE_DAYS))
        queryset = queryset.order_by('latest')

        queryset = queryset[:3]
        for persoon in queryset:
            persoon.selected = True
            persoon.save()
