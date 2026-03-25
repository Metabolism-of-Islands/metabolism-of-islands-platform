from django.urls import path
from . import views
from ie.urls_baseline import baseline_urlpatterns

app_name = "optamos"

urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
    path("login/", views.account_login, name="login"),
    path("logout/", views.account_logout, name="logout"),
    path("about/", views.about, name="about"),
    path("resources/", views.resources, name="resources"),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/", views.projects, name="projects"),
    path("projects/<int:id>/", views.project, name="project"),
    path("projects/<int:id>/results/", views.project_results, name="project_results"),
    path("projects/<int:id>/sensitivity/", views.project_results, {"page": "sensitivity"}, name="project_sensitivity"),
    path("projects/<int:id>/settings/", views.project_settings, name="project_settings"),
    path("projects/<int:id>/team/", views.project_team, name="project_team"),
    path("account/", views.account, name="account"),
    path("account/create/", views.account_create, name="account_create"),
]
