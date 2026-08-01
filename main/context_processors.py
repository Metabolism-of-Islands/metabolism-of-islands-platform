from main.models import *

def site(request):

    context = {
        "ISLANDS": Island.objects.all(),
    }
    return context
