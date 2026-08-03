from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("islands/<slug:slug>/", views.island, name="island"),
    path("islands/", views.islands, name="islands"),
    path("islands/region/", views.regions, name="regions"),
    path("islands/region/<int:region>/", views.region, name="region"),

    path("about/", views.about_overview, name="about_overview"),
    path("about/<slug:slug>/", views.about, name="about"),

    path("research/", views.research, {"slug": "projects"}, name="research"),
    path("research/<slug:slug>/", views.research, name="research"),

    path("library/", views.library, name="library"),
    path("library/browse/", views.library_list, name="library_list"),
    path("library/ajax/", views.library_ajax, name="library_ajax"),
    path("library/ajax/search/", views.library_ajax_search, name="library_ajax_search"),

    path("controlpanel/", views.controlpanel, name="controlpanel"),
    path("controlpanel/webpages/", views.controlpanel_webpages, name="controlpanel_webpages"),
    path("controlpanel/webpages/<int:id>/", views.controlpanel_webpage, name="controlpanel_webpage"),
    path("controlpanel/webpages/create/", views.controlpanel_webpage, name="controlpanel_webpage"),
    path("controlpanel/tags/", views.controlpanel_tags, name="controlpanel_webpages"),
    path("controlpanel/tags/<int:id>/", views.controlpanel_tag, name="controlpanel_tag"),
    path("controlpanel/tags/create/", views.controlpanel_tag, name="controlpanel_tag"),
    path("controlpanel/research/", views.controlpanel_research_list, name="controlpanel_research_list"),
    path("controlpanel/research/<int:id>/", views.controlpanel_research, name="controlpanel_research"),
    path("controlpanel/research/create/", views.controlpanel_research, name="controlpanel_research"),
]
