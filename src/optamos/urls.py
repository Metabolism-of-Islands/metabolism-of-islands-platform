from django.urls import path
from . import views
from ie.urls_baseline import baseline_urlpatterns

app_name = "optamos"

urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
    path("login/", views.account_login, name="login"),
    path("create/", views.project, name="project"),
]
