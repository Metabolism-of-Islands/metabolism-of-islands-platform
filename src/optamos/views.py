from core.models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import random

OPTAMOS_BG = [
    "pexels-altaf-shah-3143825-7751849.jpg",
    "pexels-ben-young-3465670-31953682.jpg",
    "pexels-ben-young-3465670-31953693.jpg",
    "pexels-kelly-2519392.jpg",
    "pexels-nacho-guillen-227263111-12041981.jpg",
    "pexels-polina-kovaleva-7648425.jpg",
    "pexels-simplyart4794-53798833-10900608.jpg",
    "pexels-stan-versluis-172635488-11034596.jpg",
    "pexels-tomfisk-1595108.jpg",
    "pexels-tomfisk-1605270.jpg",
    "pexels-tomfisk-2101137.jpg",
    "pexels-tomfisk-2246950.jpg",
    "pexels-tomfisk-3145153.jpg",
    "pexels-tomfisk-3256376.jpg",
    "pexels-tomfisk-3266775.jpg",
    "pexels-tomfisk-4198586.jpg",
    "pexels-tomfisk-5834061.jpg",
    "pexels-tomfisk-6926658.jpg",
    "pexels-tomfisk-7013401.jpg",
    "pexels-tomfisk-9940117.jpg",
    "pexels-vividcafe-681347.jpg",
]

def index(request):
    context = {
        "bg": random.choice(OPTAMOS_BG),
        "projects": OptamosProject.objects_include_private.filter(user=request.user),
    }
    return render(request, "optamos/index.html", context)

def project(request, id=None):

    project = None
    if id:
        project = OptamosProject.objects_include_private.filter(pk=id, user=request.user).first()
        if not project:
            return redirect(reverse("optamos:login"))

    context = {
        "bg": random.choice(OPTAMOS_BG),
        "projects": project,
    }
    return render(request, "optamos/index.html", context)


def account_login(request):
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        redirect_url = request.GET.get("redirect", reverse("optamos:index"))

        if user is not None:
            login(request, user)
            people = People.objects.get(user=user)
            if people.meta_data and "temporary_password" in people.meta_data:
                messages.success(request, "Please change your temporary pin. You can set your own password here:" + "<br><a href='/hub/profile/edit/?shortened=true'>" + "Edit my profile" + "</a>")
            return redirect(redirect_url)
        else:
            messages.error(request, "We could not authenticate you, please try again.")

    context = {
        "bg": random.choice(OPTAMOS_BG),
    }
    return render(request, "optamos/login.html", context)
