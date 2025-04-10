from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views
from community import views as community

from ie.urls_baseline import baseline_urlpatterns

app_name = "core"
site_url = ''
archive_url = 'https://archive.metabolismofcities.org'

urlpatterns = baseline_urlpatterns + [

    # Homepage
    path("", views.index, name="index"),

    # Templates
    path("templates/", views.templates, name="templates"),
    path("templates/folium/", views.template_folium, name="template_folium"),
    path("templates/<slug:slug>/", views.template, name="template"),

    # News
    path("news/", views.news_list, name="news"),
    path("news/<slug:slug>/", views.news, name="news"),
    path("news_events/", views.news_events_list, name="news_events"),

    # Projects
    path("projects/<slug:slug>/", views.project, name="project"),
    path("projects/", views.projects, name="projects"),
    path("pdf/", views.pdf),
    path("projects/create/", views.project_form, name="project_form"),

    # About pages
    path("about/", views.article_list, { "id": 31 }, name="about"),
    path("about/our-story/", views.ourstory, name="ourstory"),
    path("about/<slug:slug>/", views.article, { "prefix": "/about/" }, name="about"),

    # Users
    path("hub/users/", views.users, name="users"),
    path("hub/users/<int:id>/", views.user_profile, name="user"),
    path("hub/scoreboard/", views.users, {"scoreboard": True}, name="scoreboard"),
    path("hub/rules/", views.rules, name="rules"),

    # Authentication
    path("accounts/register/", views.user_register, name="register"),
    path("accounts/login/", views.user_login, name="login"),
    path("accounts/logout/", views.user_logout, name="logout"),
    path("accounts/profile/", views.user_profile, name="user_profile"),

    # Interaction links
    path("contributor/", views.contributor, name="contributor"),

    # Temporary
    path("pdf/", views.pdf),

    # Local only
    path("trim_database/", views.trim_database),
    path("search/ajax/<slug:type>/", views.search_ajax, name="search_ajax"),
    path("forum/", community.forum_list, name="forum_list"),
]
