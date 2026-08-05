from django.urls import path
from . import views

#app_name = "main" I did not use main:linkname syntax so we deactivate this. Maybe use in the future but no clear benefit now. Let's give any additional app an app_name so we just preface THOSE links, just not the main app's links

urlpatterns = [
    path("", views.index, name="index"),
    path("islands/<slug:slug>/", views.island, name="island"),
    path("islands/", views.islands, name="islands"),
    path("islands/regions/", views.regions, name="regions"),
    path("islands/regions/<slug:region>/", views.islands, name="region"),

    path("about/", views.about_overview, name="about_overview"),
    path("about/community/", views.community, name="community"),
    path("about/<slug:slug>/", views.about, name="about"),

    path("resources/", views.resources_overview, name="resources_overview"),
    path("resources/videos/", views.videos, name="videos"),
    path("resources/videos/<int:id>/", views.video, name="video"),
    path("resources/<slug:slug>/", views.resources, name="resources"),

    path("news/", views.news_overview, name="news"),
    path("news/<slug:slug>/", views.news, name="news"),

    path("events/", views.events, name="events"),
    path("events/<slug:slug>/", views.event, name="event"),

    path("research/", views.research, {"slug": "projects"}, name="research"),
    path("research/<slug:slug>/", views.research, name="research"),

    path("library/", views.library, name="library"),
    path("library/browse/", views.library_list, name="library_list"),
    path("library/ajax/", views.library_ajax, name="library_ajax"),
    path("library/ajax/search/", views.library_ajax_search, name="library_ajax_search"),
    path("library/<int:id>/", views.library_item, name="library_item"),

    #################
    # CONTROL PANEL #
    #################
    path("controlpanel/", views.controlpanel, name="controlpanel"),

    path("controlpanel/webpages/", views.controlpanel_webpages, name="controlpanel_webpages"),
    path("controlpanel/webpages/<int:id>/", views.controlpanel_webpage, name="controlpanel_webpage"),
    path("controlpanel/webpages/create/", views.controlpanel_webpage, name="controlpanel_webpage"),

    path("controlpanel/events/", views.controlpanel_events, name="controlpanel_events"),
    path("controlpanel/events/<int:id>/", views.controlpanel_event, name="controlpanel_event"),
    path("controlpanel/events/create/", views.controlpanel_event, name="controlpanel_event"),

    path("controlpanel/regions/", views.controlpanel_regions, name="controlpanel_regions"),
    path("controlpanel/regions/<int:id>/", views.controlpanel_region, name="controlpanel_region"),

    path("controlpanel/tags/", views.controlpanel_tags, name="controlpanel_tags"),
    path("controlpanel/tags/<int:id>/", views.controlpanel_tag, name="controlpanel_tag"),
    path("controlpanel/tags/create/", views.controlpanel_tag, name="controlpanel_tag"),

    path("controlpanel/research/", views.controlpanel_research_list, name="controlpanel_research_list"),
    path("controlpanel/research/<int:id>/", views.controlpanel_research, name="controlpanel_research"),
    path("controlpanel/research/create/", views.controlpanel_research, name="controlpanel_research"),

    path("controlpanel/islands/", views.controlpanel_islands, name="controlpanel_islands"),
    path("controlpanel/islands/<int:id>/", views.controlpanel_island, name="controlpanel_island"),
    path("controlpanel/islands/create/", views.controlpanel_island, name="controlpanel_island"),

    path("controlpanel/library/", views.controlpanel_library, name="controlpanel_library"),
    path("controlpanel/library/<int:id>/", views.controlpanel_library_item, name="controlpanel_library_item"),
    path("controlpanel/library/items/<int:id>/", views.controlpanel_library_items, name="controlpanel_library_items"),

    path("controlpanel/videos/", views.controlpanel_videos, name="controlpanel_videos"),

    path("controlpanel/users/", views.controlpanel_users, name="controlpanel_users"),
    path("controlpanel/users/<int:id>/", views.controlpanel_user, name="controlpanel_user"),
    path("controlpanel/users/create/", views.controlpanel_user, name="controlpanel_user"),
]
