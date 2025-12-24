from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *
from django.contrib import messages
from django.utils import timezone
import pytz

def index(request):
    context = {
        "show_project_design": True,
        "title": "Optamos",
    }
    return render(request, "optamos/index.html", context)
