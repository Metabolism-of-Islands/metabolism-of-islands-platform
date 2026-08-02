from main.models import *
from itertools import groupby
from operator import attrgetter

def site(request):

    # Try can be removed once the migration is complete
    try:
        qs = Island.objects.all().order_by("region", "name")
        regions = [
            (region, list(islands))
            for region, islands in groupby(qs, key=lambda p: p.get_region_display())
        ]

        context = {
            "REGIONS": regions,
        }
        return context
    except:
        return {}
