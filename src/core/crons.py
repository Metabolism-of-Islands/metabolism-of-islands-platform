from django_cron import CronJobBase, Schedule
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import *

TAG_ID = settings.TAG_ID_LIST

class CreateMapJS(CronJobBase):
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.createmapjs" # Unique code for logging purposes

    def do(self):
        import json
        items = LibraryItem.objects.filter(status="active", tags__id=TAG_ID["case_study"])
        city = {}
        all_cities = []
        for each in items:
            for space in each.spaces.all():
                if space.is_city and space.location:
                    city = {
                        "city": space.name,
                        "id": space.id, 
                        "lat": space.location.geometry.centroid[1],
                        "long": space.location.geometry.centroid[0],
                    }
                    all_cities.append(city)  
            
        all_cities = json.dumps(all_cities)
        file = settings.STATIC_ROOT + "js/librarymap.js"
        file = open(file, "w")
        file.write(all_cities)
        file.close()

class Notifications(CronJobBase):
    RUN_EVERY_MINS = 60

    def do(self):
        list = Notification.objects.filter(is_read=False).order_by("people_id")
        project = get_object_or_404(Project, pk=1)
        url_project = project.get_website()


        counter = 0
        last_people = 0
        info_user = {}
        last_user = 0
        url = url_project+"hub/forum/"

        messages_by_people = {}
        for notification in list:
            
            info_user[notification.people.id] = notification.people.user
            messages_by_people.setdefault(notification.people.id, []).append(notification)


        for index in messages_by_people:
            counter = counter + 1;
            print(counter)
            user = info_user[index]
            context = {
                "list": messages_by_people[index],
                "firstname": user.first_name,
                "url": url,
                "organization_name": "Metabolism of Cities",
            }

            msg_html = render_to_string("mailbody/notifications.html", context)
            msg_plain = render_to_string("mailbody/notifications.txt", context)

            sender = "Metabolismofcities" + '<info@penguinprotocols.com>'
            recipient = '"' + user.first_name + '" <' + user.email + '>'
            send_mail(
                "Your latest notifications from The Backoffice",
                msg_plain,
                sender,
                [user.email],
                html_message=msg_html,
            )