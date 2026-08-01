from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("islands/<slug:slug>/", views.island, name="island"),
    path("islands/", views.islands, name="islands"),
    path("islands/region/", views.regions, name="regions"),
    path("islands/region/<int:region>/", views.region, name="region"),
]
