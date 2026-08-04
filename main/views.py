from main.models import *
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count #, Q, Subquery, OuterRef, CharField, Avg
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.gis.geos import GEOSGeometry
from django.core.serializers import serialize
from itertools import groupby
import json

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

        elif migrate == "7":
            tags = Tag.objects.all()
            print("ALL", tags.count())
            tags = Tag.objects.annotate(record_count=Count('record')).filter(record_count=0).exclude(parent_tag__isnull=True)
            keep_tags = Tag.objects.annotate(record_count=Count('record')).filter(record_count__gt=0)
            print("Keep", keep_tags, keep_tags.count())
            print("Remove:", tags, tags.count())

            Tag.objects.filter(pk=745).delete()
            Tag.objects.filter(pk__in=[768,924,317,942,943,1751,1226,940]).delete()

            all_to_keep = []
            for each in keep_tags:
                if each.parent_tag:
                    cp = each.parent_tag
                    if cp.parent_tag:
                        cp = cp.parent_tag
                        if cp.parent_tag:
                            cp = cp.parent_tag
                            if cp.parent_tag:
                                cp = cp.parent_tag
                else:
                    cp = each
                if cp not in all_to_keep:
                    all_to_keep.append(cp)
            print(all_to_keep)

            keep = []
            for each in keep_tags:
                keep.append(each.id)

            for each in tags:
                if each.parent_tag.id not in keep:
                    grandparent = each.parent_tag.parent_tag
                    if grandparent:
                        if grandparent.id not in keep:
                            #each.delete()
                            pass
                    else:
                        #each.delete()
                        pass

            messages.success(request, "Unused tags are deleted")
        elif migrate == "8":
            Region.objects.create(name="Pacific Ocean", position=1)
            Region.objects.create(name="Caribbean", position=2)
            Region.objects.create(name="Indian Ocean", position=3)
            Region.objects.create(name="Other", position=4)
            for each in Island.objects.all():
                region = each.old_region
                each.region_id = region
                each.save()
            
            messages.success(request, "Regions are now cleaned up")

    # END OF MIGRATION CODE

    islands = Island.objects.all()
    context = {
        "islands": islands,
    }
    return render(request, "main/index.html", context)

def islands(request, region=None):
    islands = Island.objects.all()

    if region:

        # Horrific hack while we don't have a slug yet, but no real impact performance with 4 regions...
        for each in Region.objects.all():
            if slugify(each.name) == region:
                region = each

        islands = islands.filter(region=region)

    # 1. Base filtered items queryset excluding images for total counts
    items = LibraryItem.objects.exclude(type_id=38)

    # 2. Annotate islands via the parent 'record' relationship 
    # and filter down to the child 'libraryitem' subclass
    qs = islands.annotate(
        item_count=Count(
            "record__libraryitem", 
            filter=~Q(record__libraryitem__type_id=38)
        )
    ).order_by("region", "name")

    # 3. Group the annotated queryset by region
    regions = [
        (region, list(islands))
        for region, islands in groupby(qs, key=lambda p: p.region.name)
    ]
    context = {
        "islands": islands,
        "menu": "islands",
        "regions": regions,
        "region_selected": region,
    }
    return render(request, "main/islands.html", context)

def island(request, slug):
    info = get_object_or_404(Island, slug=slug)
    
    # Get all publication library items associated with this specific island
    items = LibraryItem.objects.filter(
        spaces=info
    ).exclude(
        type_id=38
    ).select_related("type").prefetch_related("tags").order_by("-year", "name")
    
    # Extract item IDs to limit sidebar counts to this specific island context
    item_ids = list(items.values_list("id", flat=True))
    
    # Aggregate only the Document Types present in this island's collection
    doc_types = LibraryItemType.objects.filter(
        items__id__in=item_ids
    ).annotate(
        island_total=Count("items", filter=Q(items__id__in=item_ids))
    ).order_by("-island_total")
    
    # Aggregate only the Tags present in this island's collection
    tags = Tag.objects.filter(
        record__libraryitem__id__in=item_ids
    ).annotate(
        island_total=Count("record__libraryitem", filter=Q(record__libraryitem__id__in=item_ids))
    ).order_by("-island_total")

    try:
        second_photo = Photo.objects.filter(spaces=info).order_by("position")[1]
    except:
        second_photo = None

    context = {
        "info": info,
        "items": items,
        "doc_types": doc_types,
        "tags": tags,
        "menu": "islands",
        "geojson": json.loads(info.geometry.geojson) if info.geometry else None,
        "bg_image": info.photo.image.large.url,
        "second_photo": second_photo,
    }

    return render(request, "main/island.html", context)

def regions(request):
    islands = Island.objects.all()
    context = {
        "islands": islands,
        "menu": "islands",
    }
    return render(request, "main/islands.html", context)

def library(request):

    # 1. Base filtered items queryset excluding images for total counts
    items = LibraryItem.objects.exclude(type_id=38)

    # 2. Annotate islands via the parent 'record' relationship 
    # and filter down to the child 'libraryitem' subclass
    qs = Island.objects.annotate(
        item_count=Count(
            "record__libraryitem", 
            filter=~Q(record__libraryitem__type_id=38)
        )
    ).order_by("region", "name")

    # 3. Group the annotated queryset by region
    regions = [
        (region, list(islands))
        for region, islands in groupby(qs, key=lambda p: p.region.name)
    ]

    context = {
        "types": LibraryItemType.objects.exclude(pk=38).annotate(total=Count("items")).filter(total__gt=0).order_by("-total"),
        "regions": regions,
        "total": items.count(),
        "menu": "library",
    }
    return render(request, "main/library.html", context)

def library_list(request, item_type=None):

    tags = (
        Tag.objects
           .annotate(record_count=Count("record"))
           .filter(record_count__gt=0)
           .select_related("parent_tag")
           .order_by("parent_tag_id", "parent_tag__name", "name")
    )

    grouped_tags = []
    for parent_tag_id, group in groupby(tags, key=lambda t: t.parent_tag_id):
        group_list = list(group)

        parent = group_list[0].parent_tag
        parent_name = parent.name if parent is not None else None

        grouped_tags.append((parent_name, group_list))

    context = {
        "item_types": LibraryItemType.objects.exclude(pk=38).annotate(total=Count("items")).filter(total__gt=0).order_by("-total"),
        "tags": grouped_tags,
        "menu": "library",
    }
    return render(request, "main/library.list.html", context)

def library_item(request, id):
    # Fetch the main item
    item = LibraryItem.objects.select_related("type", "license").get(pk=id)
    
    # Extract IDs to compare against
    island_ids = list(item.spaces.values_list("id", flat=True))
    tag_ids = list(item.tags.values_list("id", flat=True))
    
    # 1. Base filter: Exclude current item and type 38
    related_qs = LibraryItem.objects.exclude(pk=item.pk).exclude(type_id=38)
    
    # 2. Match at least one common island or tag
    related_qs = related_qs.filter(
        Q(spaces__id__in=island_ids) | Q(tags__id__in=tag_ids)
    )
    
    # 3. Calculate overlap counts to handle priority ranking
    related_items = related_qs.annotate(
        # Primary priority: Count matching islands
        same_islands_count=Count(
            "spaces", 
            filter=Q(spaces__id__in=island_ids), 
            distinct=True
        ),
        # Secondary priority: Count matching tags
        same_tags_count=Count(
            "tags", 
            filter=Q(tags__id__in=tag_ids), 
            distinct=True
        )
    ).order_by(
        "-same_islands_count",  # Highest island overlap first
        "-same_tags_count",     # Tie-breaker: Highest tag overlap
        "-year"                 # Freshness fallback
    )[:3]                       # Limit results strictly to 3
    
    context = {
        "item": item,
        "related_items": related_items,
        "menu": "library",
    }
    return render(request, "main/library.item.html", context)

@csrf_exempt
def library_ajax(request):
    island_ids = request.POST.getlist("islands[]")
    item_type_ids = request.POST.getlist("item_types[]")
    tag_ids = request.POST.getlist("tags[]")
    page_number = request.POST.get("page", 1)

    if not any([island_ids, item_type_ids, tag_ids]):
        return JsonResponse({
            "results": [],
            "total_count": 0,
            "current_page": 1,
            "total_pages": 1,
            "has_next": False,
            "has_previous": False
        })

    items = LibraryItem.objects.exclude(type_id=38)

    if island_ids:
        items = items.filter(spaces__id__in=island_ids)

    if item_type_ids:
        items = items.filter(type_id__in=item_type_ids)

    if tag_ids:
        items = items.filter(tags__id__in=tag_ids)

    items = items.distinct().select_related("type").prefetch_related("spaces")
    total_count = items.count()

    paginator = Paginator(items, 25)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    def truncate(text):
        if len(text) <= 300:
            return text
        return text[:300].rstrip() + "..."

    results_list = []
    for item in page_obj:
        results_list.append({
            "id": item.id,
            "name": item.name,
            "description": truncate(item.description) if item.description else None,
            "type": item.type.name if item.type else None,
            "year": item.year if item.year else "",
            "author": item.get_author_citation(),
            "absolute_url": item.get_absolute_url(),
            "islands": [space.name for space in item.spaces.all()],
        })

    return JsonResponse({
        "results": results_list,
        "total_count": total_count,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
    })

def library_ajax_search(request):
    """
    AJAX endpoint for searching LibraryItem records by name/title.
    URL: /ajax/library/titles/
    Expected Query Parameter: ?q=search_term
    """
    # Grab the 'q' parameter from the GET request, defaulting to an empty string
    search_query = request.GET.get("q", "").strip()
    
    # Initialize an empty results list
    results = []
    
    if search_query:
        # Filter: Exclude type_id 38 (images) AND case-insensitively match the name string.
        # Limits the evaluation row layer to 15 records maximum.
        items = LibraryItem.objects.exclude(type_id=38).filter(
            name__icontains=search_query
        ).select_related("type")[:15]
        
        for item in items:
            results.append({
                "id": item.id,
                "name": item.name,
                "year": item.year if item.year else "",
                "type": item.type.name,
                "absolute_url": item.get_absolute_url(),
            })
            
    return JsonResponse(results, safe=False)

def about_overview(request):
    islands = Island.objects.filter(region=region)
    context = {
        "islands": islands,
        "region": Island.Regions(region).label,
        "menu": "about",
    }
    return render(request, "main/islands.html", context)

def about(request, slug):
    slug = f"/about/{slug}/"
    info = Webpage.objects.get(slug=slug)
    context = {
        "info": info,
        "menu": "about",
    }
    return render(request, "main/about.html", context)

def news_overview(request):
    news = News.objects.all()
    context = {
        "menu": "news",
        "news": news,
        "years": news.dates("date", "year", order="DESC"),
    }
    return render(request, "main/news.overview.html", context)

def news(request, slug):
    info = get_object_or_404(News, slug=slug)
    context = {
        "info": info,
        "menu": "news",
        "latest": News.objects.all()[:5],
    }
    return render(request, "main/news.html", context)

def events(request):
    events = Event.objects.all()
    context = {
        "menu": "events",
        "events": events,
        "years": events.dates("start_date", "year", order="DESC"),
    }
    return render(request, "main/events.html", context)

def event(request, slug):
    info = get_object_or_404(Event, slug=slug)
    context = {
        "info": info,
        "menu": "news",
        "latest": Event.objects.all()[:5],
    }
    return render(request, "main/event.html", context)

def research(request, slug):
    project_type = "thesis" if slug == "theses" else "research"
    slug = f"/research/{slug}/"
    info = Webpage.objects.get(slug=slug)
    context = {
        "info": info,
        "projects": PublicProject.objects.filter(project_type=project_type),
        "menu": "research",
    }
    return render(request, "main/research.html", context)

# Control Panel section
def controlpanel(request):
    context = {
    }
    return render(request, "main/controlpanel/index.html", context)

def controlpanel_islands(request):
    context = {
        "pages": Island.objects.all(),
    }
    return render(request, "main/controlpanel/islands.html", context)

def controlpanel_island(request, id=None):

    if id:
        info = get_object_or_404(Island, pk=id)
    else:
        info = None

    if request.method == "POST":
        # Extract plain parameters from text form bindings
        name = request.POST.get("name", "").strip()
        region_id = request.POST.get("region")
        wkt_geometry = request.POST.get("geometry")
        
        # Instantiate instance parameters
        if not info:
            info = Island()
        
        info.name = name
        info.region = get_object_or_404(Region, pk=region_id) if region_id else None
        
        # Handle standard map input conversion to Point geometries safely
        if wkt_geometry:
            try:
                info.geometry = GEOSGeometry(wkt_geometry)
            except (ValueError, TypeError):
                messages.error(request, "Invalid spatial coordinate data schema submitted.")
        
        # Save media files if newly supplied, preserving fallback paths if blank
        if "primary_image" in request.FILES:
            info.primary_image = request.FILES["primary_image"]
        if "secondary_image" in request.FILES:
            info.secondary_image = request.FILES["secondary_image"]
            
        info.save()
        messages.success(request, f"Successfully saved profile for {info.name}.")
        return redirect("/controlpanel/islands/")

    # Compile a GeoJSON payload if a non-Point geometry (like a structural shapefile outline) exists
    geojson_payload = "{}"
    if info and info.geometry:
        if info.geometry.geom_type != "Point":
            geojson_payload = serialize("geojson", [info], geometry_field="geometry")
            # Unpack feature array wrapper string to match leaflet inline initialization parameters
            try:
                features_list = json.loads(geojson_payload).get("features", [])
                if features_list:
                    geojson_payload = json.dumps(features_list[0].get("geometry", {}))
            except json.JSONDecodeError:
                geojson_payload = "{}"

    context = {
        "info": info,
        "regions": Region.objects.all(),
        "geojson": geojson_payload,
    }
    return render(request, "main/controlpanel/island.html", context)

def controlpanel_library(request):
    context = {
        "types": LibraryItemType.objects.all(),
    }
    return render(request, "main/controlpanel/library.html", context)

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

def controlpanel_tags(request):
    context = {
        "tags": Tag.objects.all(),
    }
    return render(request, "main/controlpanel/tags.html", context)

def controlpanel_tag(request, id=None):

    if id:
        info = Tag.objects.get(pk=id)

    context = {
        "info": info,
    }
    return render(request, "main/controlpanel/tag.html", context)
