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
import requests
from django.core.files.base import ContentFile

def index(request):
    islands = Island.objects.all()
    regions = Region.objects.all().order_by("position").annotate(island_count=Count("islands"))
    context = {
        "islands": islands,
        "regions": regions,
        "news": News.objects.all()[:3],
        "library": LibraryItemType.objects.exclude(pk=38).annotate(total=Count("items")).filter(total__gt=0).order_by("-total")[:3],
        "library_size": LibraryItem.objects.exclude(type__id=38).count(),
        #"video": Video.objects.get(pk=1280307),
        #"video_highlights": Video.objects.filter(pk__in=[1280309,642031,1280308]),
        "video_library_size": Video.objects.all().count(),
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
    context = {
        "menu": "about",
    }
    return render(request, "main/about.overview.html", context)

def about(request, slug):
    slug = f"/about/{slug}/"
    info = Webpage.objects.get(slug=slug)
    context = {
        "info": info,
        "menu": "about",
    }
    return render(request, "main/about.html", context)

def resources_overview(request):
    context = {
        "menu": "resources",
    }
    return render(request, "main/resources.overview.html", context)

def videos(request):

    context = {
        "menu": "resources",
        "page": "videos",
        "videos": Video.objects.all(),
    }
    return render(request, "main/videos.html", context)

def video(request, id):
    context = {
        "menu": "resources",
        "page": "videos",
        "info": LibraryItem.objects.get(pk=id),
        "videos": LibraryItem.objects.filter(type__name="Video Recording").order_by("-date_created")[:5],
    }
    return render(request, "main/video.html", context)

def resources(request, slug):
    slug = f"/resources/{slug}/"
    info = Webpage.objects.get(slug=slug)
    context = {
        "info": info,
        "menu": "resources",
    }
    return render(request, "main/resources.html", context)

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
        "menu": "events",
        "latest": Event.objects.all().order_by("start_date")[:5],
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
        if "deactivate" in request.POST:
            info.is_deleted = True
            info.save()
            messages.success(request, f"{info.name} was deactivated.")
            return redirect("/controlpanel/islands/")

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

def controlpanel_library_items(request, id):
    item_type = LibraryItemType.objects.get(pk=id)
    items = LibraryItem.objects.filter(type=item_type)
    context = {
        "info": item_type,
        "items": items,
    }
    return render(request, "main/controlpanel/library.items.html", context)

def controlpanel_library_item(request, id):
    if id:
        info = LibraryItem.objects.get(pk=id)
    context = {
        "types": LibraryItemType.objects.all(),
        "tags": Tag.objects.all(),
        "licenses": License.objects.all(),
        "islands": Island.objects.all(),
        "info": info,
        "languages": LibraryItem.LANGUAGES,
    }
    return render(request, "main/controlpanel/library.item.html", context)

def controlpanel_videos(request):

    # Temp code until we finish migration
    for each in LibraryItem.objects.filter(type_id=31):
        if not hasattr(each, "video"):
            sql = f"INSERT INTO main_video (libraryitem_ptr_id) VALUES ({each.pk});"
            messages.warning(request, sql)
    # end temp code


    if request.method == "POST":

        url = request.POST["url"]

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": False,
        }

        from yt_dlp import YoutubeDL
        with YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=False)

        video = Video.objects.create(
            name=data.get("title", ""),
            description=data.get("description", ""),
            duration=int((data.get("duration") or 0) / 60),
            author_list=data.get("uploader", ""),
            url=url,
            date=data.get("upload_date"),
            type_id=31,
        )

        thumbnail = data.get("thumbnail")

        if thumbnail:
            response = requests.get(thumbnail, timeout=20)

            if response.status_code == 200:
                filename = f"{video.pk}.jpg"
                video.image.save(
                    filename,
                    ContentFile(response.content),
                    save=True,
                )

        messages.success(request, "The video has been added. You can review it below.")
        return redirect(video.get_absolute_url())

    context = {
        "videos": Video.objects.all(),
    }
    return render(request, "main/controlpanel/videos.html", context)

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

def controlpanel_events(request):
    context = {
        "events": Event.objects.all(),
    }
    return render(request, "main/controlpanel/events.html", context)

def controlpanel_event(request, id=None):

    if id:
        info = Event.objects.get(pk=id)

    context = {
        "info": info,
    }
    return render(request, "main/controlpanel/event.html", context)

def controlpanel_users(request):
    context = {
        "users": User.objects.filter(last_login__isnull=False).order_by("-last_login"),
    }
    return render(request, "main/controlpanel/users.html", context)

def controlpanel_user(request, id=None):
    if id:
        user = User.objects.get(pk=id)
    else:
        user = User()
    context = {
        "user": user,
        "islands": Island.objects.all(),
    }
    return render(request, "main/controlpanel/user.html", context)

