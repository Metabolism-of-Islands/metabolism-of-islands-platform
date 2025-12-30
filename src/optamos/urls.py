from django.urls import path
from . import views
from ie.urls_baseline import baseline_urlpatterns

app_name = "optamos"

urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
    path("login/", views.account_login, name="login"),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/", views.projects, name="projects"),
    path("projects/<int:id>/", views.project, name="project"),
    path("projects/<int:id>/settings/", views.project_settings, name="project_settings"),
    path("account/", views.account, name="account"),
    path("account/create/", views.account_create, name="account_create"),
]
