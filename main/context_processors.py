from main.models import *
from itertools import groupby
from operator import attrgetter

def site(request):

    qs = Island.objects.all().order_by("region", "name")
    regions = [
        (region, list(islands))
        for region, islands in groupby(qs, key=lambda p: p.region.name)
    ]

    context = {
        "REGIONS": regions,
    }
    return context
