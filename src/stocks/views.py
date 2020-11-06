from django.shortcuts import render
from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.forms import modelform_factory
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.cache import cache_page

from django.utils import timezone
import pytz

import pandas as pd
import branca

from django.db.models import Q

from core.mocfunctions import *

#from folium import Map
import folium


# temporary landing until section is ready
def landing(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "stocks/landing.html", context)

def index(request):
    context = {
    }
    return render(request, "stocks/index.html", context)

def contribute(request):
    context = {
    }
    return render(request, "stocks/contribute.html", context)

def cities(request):
    context = {
    }
    return render(request, "stocks/cities.html", context)

def city(request, slug):
    context = {
        "city": True,
    }
    return render(request, "stocks/city.html", context)

def data(request, slug):
    context = {
        "data": True,
        "load_datatables": True,
        "load_select2": True,
    }
    return render(request, "stocks/data.html", context)

def archetypes(request, slug):
    context = {
        "archetypes": True,
    }
    return render(request, "stocks/archetypes.html", context)

def maps(request, slug):
    context = {
        "map": True,
        "load_select2": True,
    }
    return render(request, "stocks/maps.html", context)

def map(request, slug, id, box=None):
    info = LibraryItem.objects.get(pk=id)
    space = ActivatedSpace.objects.all()[0]

    if box:
        box = ReferenceSpace.objects.get(pk=box)

    links = {
        # Melbourne
        33931: 33962,
        33962: 33940,

        # Brussels
        33886: 33895,
        33895: 33913,
    }

    link = links.get(id)

    spaces = info.imported_spaces.all()
    if box:
        spaces = spaces.filter(geometry__within=box.geometry)

    if spaces.count() > 100:
        pass
        #spaces = spaces[:100]

    map = None
    if spaces:

        features = []

        import random
        for each in spaces:
            features.append({
                "type": "Feature",
                "id": each.id,
                "properties": {
                    "space_name": each.name,
                    "quantity": random.randint(1,200),
                    "unit": "kg",
                    "date": "2011",
                },
                "geometry": json.loads(each.geometry.json)
            })

        data = {
            "type":"FeatureCollection",
            "features": features,
        }

    context = {
        "info": info,
        "spaces": spaces,
        "map": map._repr_html_() if map else None,
        "data": data,
        "link": link,
        "space": space,
        "box": box,
        "load_datatables": True,
    }

    return render(request, "stocks/map.html", context)

def choropleth(request):

    info = LibraryItem.objects.get(pk=33886)
    project = get_object_or_404(Project, pk=request.project)

    # We need to remove trailing slash from the get_website, to avoid double slashes
    geojson = project.get_website(True)[:-1] + reverse(project.slug + ":shapefile_json", args=[info.id])

    # Here is to show you which URL is being loaded -- check the terminal output
    p(geojson)

    state_unemployment = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/US_Unemployment_Oct2012.csv"
    state_data = pd.read_csv(state_unemployment)

    map = folium.Map(location=[48, -102], zoom_start=3)

    folium.Choropleth(
        geo_data=geojson,
        name='choropleth',
        data=state_data,
        columns=['State', 'Unemployment'],
        key_on='feature.id',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Unemployment Rate (%)'
    ).add_to(map)

    folium.LayerControl().add_to(map)

    context = {
        "map": map._repr_html_() if map else None,
    }

    return render(request, "stocks/map.html", context)

def compare(request, slug):
    context = {
        "compare": True,
        "load_select2": True,
    }
    return render(request, "stocks/compare.html", context)

def modeller(request, slug):
    context = {
        "modeller": True,
    }
    return render(request, "stocks/modeller.html", context)

def stories(request, slug):
    context = {
        "stories": True,
    }
    return render(request, "stocks/stories.html", context)

def story(request, slug, title):
    context = {
        "stories": True,
    }
    return render(request, "stocks/story.html", context)

def dataset_editor(request):
    context = {
    }
    return render(request, "stocks/dataset-editor/index.html", context)

def chart_editor(request):
    context = {
    }
    return render(request, "stocks/dataset-editor/chart.html", context)

def map_editor(request):
    context = {
    }
    return render(request, "stocks/dataset-editor/map.html", context)
