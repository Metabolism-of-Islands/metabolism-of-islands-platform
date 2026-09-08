from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from main.models import *

# sudo docker exec -it metabolismofislands_web python /code/manage.py zoteroimport --- run locally
# Runs on the server once a day

class Command(BaseCommand):
    help = "We check the Zotero collection to see if there are any new items and if so, we import them into the database"

    def handle(self, *args, **options):

        collection = ZoteroCollection.objects.all().first()
    
        api = collection.api
        zotero_id = collection.zotero_id

        zot = zotero.Zotero(zotero_id, "group", api)
        publication_list = zot.top(limit=5)
        #publication_list = zot.everything(zot.top())
        print(publication_list)

        for each in publication_list:
            try:
                info = ZoteroItem.objects.get(key=each["data"].get("key"))
                info.data = each["data"]
                info.save()
                print("FOUND!", info)
            except:
                title = each["data"].get("title")
                info = ZoteroItem.objects.create(
                    title = title[:255] if title else "No title", # Truncate the title to make sure the title length does not exceed 255 characters
                    key = each["data"].get("key"),
                    data = each["data"],
                    collection = collection,
                )
                print("NEW!", info)
            info.import_to_library()
