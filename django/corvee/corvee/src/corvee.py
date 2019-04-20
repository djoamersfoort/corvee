from .models import Persoon
from django.conf import settings
import requests


class Corvee:

    @staticmethod
    def update_members(access_token):
        response = requests.get(settings.LEDEN_ADMIN_API_URL,
                                headers={'Authorization': 'IDP {0}'.format(access_token)})
        if response.ok:
            Persoon.objects.all().update(marked_for_deletion=True)

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
