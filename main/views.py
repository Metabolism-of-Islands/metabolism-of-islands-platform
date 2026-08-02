from django.shortcuts import render
from django.contrib import messages
from main.models import *

def index(request):

    # TEMP MIGRATION CODE

    if "migrate" in request.GET:
        migrate = request.GET["migrate"]
        if migrate == "1":
            ReferenceSpace.objects.filter(activated__isnull=True).delete()
            messages.success(request, "Non-activated reference spaces are deleted; only islands remain")
        elif migrate == "2":
            regions = [
                ("AIMS Region", "Other"),
                ("American Samoa", "Pacific Ocean"),
                ("Antigua & Barbuda", "Caribbean"),
                ("Aruba", "Caribbean"),
                ("Bahamas", "Caribbean"),
                ("Barbados", "Caribbean"),
                ("Belize", "Caribbean"),
                ("British Virgin Islands", "Caribbean"),
                ("Cabo Verde", "Other"),
                ("Canary Islands", "Other"),
                ("Caribbean Region", "Other"),
                ("Comoros", "Indian Ocean"),
                ("Cook Islands", "Pacific Ocean"),
                ("Crete", "Other"),
                ("Cuba", "Caribbean"),
                ("Curacao", "Caribbean"),
                ("Cyprus", "Other"),
                ("Dominica", "Caribbean"),
                ("Dominican Republic", "Caribbean"),
                ("Faroe Islands", "Other"),
                ("Fiji", "Pacific Ocean"),
                ("Galapagos Islands", "Pacific Ocean"),
                ("Grenada", "Caribbean"),
                ("Guadeloupe", "Caribbean"),
                ("Guam", "Pacific Ocean"),
                ("Guinea-Bissau", "Other"),
                ("Guyana", "Other"),
                ("Haiti", "Caribbean"),
                ("Hawaii", "Pacific Ocean"),
                ("Hong Kong", "Other"),
                ("Jamaica", "Caribbean"),
                ("Kiribati", "Pacific Ocean"),
                ("Madagascar", "Indian Ocean"),
                ("Maldives", "Indian Ocean"),
                ("Mallorca", "Other"),
                ("malta", "Other"),
                ("Marshall Islands", "Pacific Ocean"),
                ("Martinique", "Caribbean"),
                ("Mauritius", "Indian Ocean"),
                ("Micronesia", "Pacific Ocean"),
                ("Nauru", "Pacific Ocean"),
                ("New Caledonia", "Pacific Ocean"),
                ("Niue", "Pacific Ocean"),
                ("Northern Mariana Islands (CNMI)", "Pacific Ocean"),
                ("Oahu", "Pacific Ocean"),
                ("Okinawa", "Pacific Ocean"),
                ("Pacific Region", "Other"),
                ("Palau", "Pacific Ocean"),
                ("Papua New Guinea", "Pacific Ocean"),
                ("Réunion Island", "Indian Ocean"),
                ("Saint Kitts and Nevis", "Caribbean"),
                ("Saint Lucia", "Caribbean"),
                ("Saint Vincent and the Grenadines", "Caribbean"),
                ("Samoa", "Pacific Ocean"),
                ("Samothraki Island", "Other"),
                ("Sardinia", "Other"),
                ("Seychelles", "Indian Ocean"),
                ("Singapore", "Indian Ocean"),
                ("Sint Maarten", "Caribbean"),
                ("Solomon Islands", "Pacific Ocean"),
                ("Timor-Leste", "Other"),
                ("Tonga", "Pacific Ocean"),
                ("Trinidad and Tobago", "Caribbean"),
                ("Trinket Island", "Other"),
                ("Tuvalu", "Pacific Ocean"),
                ("Vanuatu", "Pacific Ocean"),
            ]
            regions = dict(regions)
            islands = Island.objects.all()
            for each in islands:
                e = str(each)
                e = e.strip()
                region = regions[e]
                if region == "Pacific Ocean":
                    each.region = 1
                elif region == "Caribbean":
                    each.region = 2
                elif region == "Other":
                    each.region = 4
                elif region == "Indian Ocean":
                    each.region = 3
                each.save()
            messages.success(request, "Regions saved")

        elif migrate == "3":
            for each in Island.objects.all():
                space = each.space
                space.region = each.region
                space.slug = each.slug
                space.save()
            messages.success(request, "Data copied from Island to ReferenceSpace; you can now remove Island and then rename")

        elif migrate == "4":
            coords = {
                "Antigua & Barbuda": (17.0608, -61.7964),
                "Aruba": (12.5211, -69.9683),
                "Cabo Verde": (15.1111, -23.6167),
                "Canary Islands": (28.2916, -16.6291),
                "Comoros ": (-11.8750, 43.8722),
                "Crete": (35.2401, 24.8093),
                "Cuba": (21.5218, -77.7812),
                "Curacao": (12.1696, -68.9900),
                "Faroe Islands": (62.0676, -6.9118),
                "Fiji": (-17.7134, 178.0650),
                "Galapagos Islands": (-0.9538, -90.9656),
                "Haiti": (18.9712, -72.2852),
                "Hawaii": (20.7984, -156.3319),
                "Mallorca": (39.6953, 3.0176),
                "malta": (35.9375, 14.3754),
                "Micronesia": (6.8875, 158.2151),
                "New Caledonia": (-21.2990, 165.4880),
                "Northern Mariana Islands (CNMI)": (15.2000, 145.7500),
                "Okinawa": (26.3344, 127.8056),
                "Pacific Region": (0.0000, -160.0000),
                "Réunion Island": (-21.1151, 55.5364),
                "Sardinia": (40.1209, 9.0129),
                "Sint Maarten": (18.0425, -63.0548),
                "Grenada": (12.1165, -61.6790),
                "Guinea-Bissau": (11.8037, -15.1804),
                "Kiribati": (1.8709, -157.3630),
            }
            from django.contrib.gis.geos import Point
            for each,cr in coords.items():
                lat, lng = cr
                try:
                    info = Island.objects.get(name=each)
                    info.name = each.strip()
                    info.geometry = Point(lng, lat, srid=4326)
                    info.save()
                except:
                    print(f"Not found, {each}")
            messages.success(request, "Coordinates are set for those that were missing.")
        elif migrate == "5":
            pages_to_keep = [51385, 31884, 1280158, 31882, 31887, 31888, 31879, 31885, 31881, 31886, 31880]
            Webpage.objects.all().exclude(pk__in=pages_to_keep).delete()
            messages.success(request, "Web page list is cleaned up")

            Webpage.objects.filter(pk__in=[31879, 51385, 31884, 31882, 31880, 31881]).update(section="about")
            research = Webpage.objects.get(pk=31886)
            research.section = "research"
            research.slug = "/research/theses/"
            research.save()
            research = Webpage.objects.get(pk=31885)
            research.section = "research"
            research.slug = "/research/projects/"
            research.save()
            messages.success(request, "Research & about sections configured")
        elif migrate == "6":
            PublicProject.objects.filter(part_of_project_id=1).delete()
            PublicProject.objects.filter(part_of_project_id__isnull=True).delete()
            messages.success(request, "Public projects are now cleaned up")

    # END OF MIGRATION CODE

    islands = Island.objects.all()
    context = {
        "islands": islands,
    }
    return render(request, "main/index.html", context)

def islands(request):
    islands = Island.objects.all()
    context = {
        "islands": islands,
    }
    return render(request, "main/islands.html", context)

def island(request, slug):
    info = Island.objects.get(slug=slug)
    context = {
        "info": info,
    }
    return render(request, "main/island.html", context)

def regions(request):
    islands = Island.objects.all()
    context = {
        "islands": islands,
    }
    return render(request, "main/islands.html", context)

def region(request, region):
    islands = Island.objects.filter(region=region)
    context = {
        "islands": islands,
        "region": Island.Regions(region).label,
    }
    return render(request, "main/islands.html", context)

def about_overview(request):
    islands = Island.objects.filter(region=region)
    context = {
        "islands": islands,
        "region": Island.Regions(region).label,
    }
    return render(request, "main/islands.html", context)

def about(request, slug):
    slug = f"/about/{slug}/"
    info = Webpage.objects.get(slug=slug)
    context = {
        "info": info,
    }
    return render(request, "main/about.html", context)

def research(request, slug):
    project_type = "thesis" if slug == "theses" else "research"
    slug = f"/research/{slug}/"
    info = Webpage.objects.get(slug=slug)
    context = {
        "info": info,
        "projects": PublicProject.objects.filter(project_type=project_type),
    }
    return render(request, "main/research.html", context)

# Control Panel section
def controlpanel(request):
    context = {
    }
    return render(request, "main/controlpanel/index.html", context)

def controlpanel_webpages(request):
    context = {
        "pages": Webpage.objects.all(),
    }
    return render(request, "main/controlpanel/pages.html", context)

def controlpanel_webpage(request, id=None):

    if id:
        info = Webpage.objects.get(pk=id)

    context = {
        "info": info,
    }
    return render(request, "main/controlpanel/page.html", context)

def controlpanel_research_list(request):
    context = {
        "research": PublicProject.objects.all(),
    }
    return render(request, "main/controlpanel/research.list.html", context)

def controlpanel_research(request, id=None):

    if id:
        info = PublicProject.objects.get(pk=id)

    context = {
        "info": info,
    }
    return render(request, "main/controlpanel/research.html", context)
