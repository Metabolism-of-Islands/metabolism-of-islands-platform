from django.urls import path
from . import views
from ie.urls_baseline import baseline_urlpatterns

app_name = "optamos"

urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
    path("login/", views.account_login, name="login"),
    path("create/", views.project_settings, name="create"),
    path("project/<int:id>/", views.project, name="project"),
    path("project/<int:id>/settings/", views.project_settings, name="project_settings"),
]
