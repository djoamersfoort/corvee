from .models import Persoon, LastSync
from django.conf import settings
from datetime import date
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
                    if not 'member' in member['types'] and not 'strippenkaart' in member['types']:
                        continue

                    try:
                        persoon = Persoon.objects.get(id=member['id'])
                    except Persoon.DoesNotExist:
                        persoon = Persoon()
                    persoon.id = member['id']
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
