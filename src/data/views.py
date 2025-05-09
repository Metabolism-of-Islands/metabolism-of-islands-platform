from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.forms import modelform_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

from django.utils import timezone
import pytz
from functools import wraps

from django.views.decorators.clickjacking import xframe_options_exempt
from core.mocfunctions import *
import random
import json

def index(request):
 
    project = get_object_or_404(Project, pk=request.project)
    id_list = ReferenceSpace.objects.filter(activated__part_of_project_id=request.project, image__isnull=False, meta_data__progress__counter__gte=1).values_list("id", flat=True)
    selected = random.sample(list(id_list), 3)
    objects = ReferenceSpace.objects.filter(id__in=selected)

    # Same block is included in index.html
    spaces = ReferenceSpace.objects.filter(activated__part_of_project=project, geometry__isnull=False)
    features = []

    # We should cache this block!
    for each in spaces:
        geo = each.geometry.centroid
        url = reverse(project.slug + ":dashboard", args=[each.slug])

        content = ""
        if each.image:
            content = f"<a class='d-block' href='{url}'><img alt='{each.name}' src='{each.get_thumbnail}' /></a><hr>"
        content = content + f"<a href='{url}'>View details</a>"

        try:
            features.append({
                "type": "Feature",
                "geometry": json.loads(geo.json),
                "properties": {
                    "name": each.name,
                    "id": each.id,
                    "content": content,
                    "color": "",
                },
            })
        except Exception as e:
            messages.error(request, f"We had an issue reading one of the items which had an invalid geometry ({each}). Error: {str(e)}")

    data = {
        "type":"FeatureCollection",
        "features": features,
        "geom_type": "Point",
    }

    context = {
        "load_leaflet": True,
        "load_leaflet_item": True,
        "load_datatables": True,
        "spaces": spaces,
        "data": data,
        "show_project_design": True,
        "list": objects,
        "layers": get_layers(request),
        "layers_count": get_layers_count(request),
        "webpage": Webpage.objects.get(pk=37077),
        "dashboard_link": project.slug + ":dashboard",
        "harvesting_link": project.slug + ":hub_harvesting_space",
        "total": ActivatedSpace.objects.filter(part_of_project_id=request.project).count(),
        "show_all": True,
    }
    return render(request, "data/index.html", context)

def overview(request):
    list = ActivatedSpace.objects.filter(part_of_project_id=request.project)
    context = {
        "list": list,
    }
    return render(request, "data/overview.html", context)

def progress(request, style="list"):
    islands = ReferenceSpace.objects.filter(activated__part_of_project_id=request.project)
    project = get_object_or_404(Project, pk=request.project)
    
    if request.GET.get("sort") == "documents":
        islands = islands.order_by("-meta_data__progress__document_counter", "name")
    elif request.GET.get("sort") == "percentage":
        islands = islands.order_by("-meta_data__progress__completion", "name")

    context = {
        "dashboard_link": project.slug + ":dashboard",
        "harvesting_link": project.slug + ":hub_harvesting_space",
        "list": islands,
        "layers": get_layers(request),
        "layers_count": get_layers_count(request),
    }

    if style == "list":
        page = "data/progress.html"
    else:
        page = "data/progress.details.html"

    return render(request, page, context)

def dashboard(request, space):
    space = get_space(request, space)
    project = get_object_or_404(Project, pk=request.project)

    list = LibraryItem.objects.filter(spaces=space)
    layers = get_layers(request)

    highscore = Work.objects.filter(related_to__spaces=space, status=Work.WorkStatus.COMPLETED) \
        .values("assigned_to__name") \
        .annotate(total=Sum("workactivity__points")) \
        .order_by("-total")

    last_fourteen_days = datetime.datetime.now() - datetime.timedelta(days=14)
    added = LibraryItem.objects.filter(spaces=space, date_created__gte=last_fourteen_days).count()

    try:
        second_photo = Photo.objects.filter(spaces=space).order_by("position")[1]
    except:
        second_photo = None

    doc_counter = {}
    list = LibraryItem.objects.filter(spaces=space)
    doc_counter["datasets"] = list.filter(type__id=10).count()
    doc_counter["maps"] = list.filter(type__id__in=[40,41,20]).count()
    doc_counter["multimedia"] = list.filter(type__group="multimedia").count()
    doc_counter["publications"] = list.filter(type__group__in=["academic", "reports"]).count()

    context = {
        "space": space,
        "header_image": space.photo,
        "dashboard": True,
        "layers": layers,
        "layers_count": get_layers_count(request),
        "done": ["collected", "processed", ""],
        "highscore": highscore[0] if highscore else None,
        "added": added,
        "second_photo": second_photo,
        "doc_counter": doc_counter,
    }
    return render(request, "data/dashboard.html", context)

def instructionvideos(request, space, layer):
    space = get_space(request, space)
    layer = Tag.objects.get(parent_tag_id=845, slug=layer)
    videos = Video.objects.filter(tags__id=754) # Filter the instruction videos section first
    videos = videos.filter(Q(tags=layer)|Q(tags__parent_tag=layer)).distinct()

    context = {
        "space": space,
        "layer": layer,
        "list": videos,
    }
    return render(request, "data/instructionvideos.html", context)

def users(request, space, scoreboard=False):

    webpage = get_object_or_404(Webpage, pk=54)
    space = get_space(request, space)

    if scoreboard:
        page = "scoreboard"
    else:
        page = "users"

    project = None
    if request.project != 1:
        project = request.project
    if "project" in request.GET:
        project = request.GET.get("project")

    # Crazy CPU load with this list, no idea why
    # Let's disable for now
    #list = People.objects.filter(message_list__isnull=False, user__isnull=False)
    #list = list.filter(message_list__parent__work__related_to__spaces=space)
    #list = list.distinct().order_by("-user__date_joined")
    list = None

    context = {
        "webpage": webpage,
        "list": list,
        "title": "People",
        "load_datatables": True,
        "menu": page,
        "space": space,
    }
    return render(request, "contribution/" + page + ".html", context)

def photos(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "photos": Photo.objects.filter(spaces=space),
        "menu": "library",
    }
    return render(request, "data/photos.html", context)

def maps(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "library",
    }
    return render(request, "data/maps.html", context)

def library(request, space, type):
    space = get_space(request, space)
    list = LibraryItem.objects.filter(spaces=space)
    if type == "articles":
        title = "Journal articles"
        list = list.filter(type__group="academic")
    elif type == "reports":
        list = list.filter(type__group="reports")
        title = "Reports"
    elif type == "theses":
        list = list.filter(type__group="theses")
        title = "Theses"
    context = {
        "space": space,
        "header_image": space.photo,
        "title": title,
        "items": list,
        "load_datatables": True,
        "menu": "library",
    }
    return render(request, "data/library.html", context)

def sector(request, space, sector):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "industries",
    }
    return render(request, "data/sector.html", context)

def article(request, space, slug):
    space = get_space(request, space)
    items = LibraryItem.objects.filter(spaces=space).filter(type__group="academic")
    info = DataArticle.objects.get(slug=slug)
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "industries",
        "load_lightbox": True,
        "items": items,
        "info": info,
        "title": info.name,
    }
    return render(request, "data/article.html", context)

def sectors(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "industries",
    }
    return render(request, "data/sector.html", context)

def datasets(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "data",
        "items": LibraryItem.objects.filter(type__name="Dataset", spaces=space),
    }
    return render(request, "data/datasets.html", context)

def eurostat(request):

    from django.core.paginator import Paginator
    page = "regular"

    hits = 1000
    if "full" in request.GET or request.GET.get("show") == "full":
        hits = 10000
        page = "full"

    full_list = EurostatDB.objects.filter(is_duplicate=False).order_by("id")
    full_list = full_list.exclude(code__startswith="med_")
    full_list = full_list.exclude(code__startswith="cpc_")
    full_list = full_list.exclude(code__startswith="enpr_")

    if "accepted" in request.GET or request.GET.get("show") == "accepted":
        full_list = full_list.filter(is_approved=True).exclude(type="folder")
        page = "accepted"

    if "pending" in request.GET or request.GET.get("show") == "pending":
        full_list = full_list.filter(is_reviewed=False).exclude(type="folder")
        page = "pending"

    if "q" in request.GET and request.GET.get("q"):
        full_list = full_list.filter(Q(title__icontains=request.GET.get("q"))|(Q(code__icontains=request.GET.get("q"))))

    paginator = Paginator(full_list, hits)
    page_number = request.GET.get("page")
    list = paginator.get_page(page_number)

    if request.user.is_authenticated and request.user.is_staff:
        if "action" in request.GET:
            try:
                info = EurostatDB.objects.get(pk=request.GET["id"])
                info.is_reviewed = True
                if request.GET["action"] == "deny":
                    info.is_denied = True
                    info.is_approved = False
                else:
                    info.is_denied = False
                    info.is_approved = True
                info.save()
                return JsonResponse({"status":"OK"})
            except:
                return JsonResponse({"status":"Fail"})

        if "deadlink" in request.GET:
            info = EurostatDB.objects.get(pk=request.GET["deadlink"])
            info.has_no_meta_data = True
            info.save()
            return JsonResponse({"status":"OK"})

    progress = full_list.filter(is_reviewed=True).count()
    no_folders = full_list.exclude(type="folder")
    percentage = progress/no_folders.count() if no_folders else 0

    context = {
        "list": list,
        "title": "Eurostat database manager",
        "progress": progress,
        "percentage": percentage*100,
        "full_list": full_list,
        "no_folders": no_folders,
        "page": page,
        "webpage": Webpage.objects.get(slug="/eurostat/"),
    }

    if "full" in request.GET or request.GET.get("show") == "full" or "accepted" in request.GET:
        context["load_datatables"] = True

    return render(request, "temp.eurostat.html", context)

