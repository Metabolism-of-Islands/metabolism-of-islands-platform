from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import *

# Contrib imports
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site

from django.db.models import Count
from django.db.models import Q

from django.http import JsonResponse, HttpResponse
from django.http import Http404, HttpResponseRedirect

from markdown import markdown

# These are used so that we can send mail
from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template

from django.conf import settings

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from collections import defaultdict

from django.template import Context
from django.forms import modelform_factory

from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from datetime import datetime
import csv

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.utils import construct_change_message
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone
import pytz

from functools import wraps
import json

# Social media imports
import twitter
import facebook

from .mocfunctions import *

THIS_PROJECT = PROJECT_ID["core"]

def user_register(request, project="core", section=None):
    people = user = is_logged_in = None
    project = get_object_or_404(Project, pk=request.project)

    if request.GET.get("next"):
        redirect_url = request.GET.get("next")
    elif project:
        redirect_url = project.get_website()
    else:
        redirect_url = "core:index"

    if request.user.is_authenticated:
        is_logged_in = True
        return redirect(redirect_url)

    if request.method == "POST":
        error = None
        password = request.POST.get("password")
        email = request.POST.get("email")
        name = request.POST.get("name")
        if request.POST.get("tw").lower() != "hello":
            messages.error(request, "Please enter 'hello' in the last box.")
            error = True
        if not password:
            messages.error(request, "You did not enter a password.")
            error = True
        check = User.objects.filter(email=email)
        if check:
            current_site = PROJECT_LIST["core"]["url"]
            messages.error(request, "A Metabolism of Cities account already exists with this e-mail address. Please <a href='/accounts/login/'>log in first</a> or <a href='" + current_site + "accounts/passwordreset/'>reset your password</a>.")
            error = True
        if not error:
            user = User.objects.create_user(email, email, password)
            user.first_name = name
            user.is_superuser = False
            user.is_staff = False
            user.save()
            login(request, user)

            people = People.objects.create(name=name, email=user.email, description=request.POST.get("background"))

            if "photo" in request.FILES and request.FILES["photo"]:
                people.image = request.FILES["photo"]

            people.user = user
            meta_data = {}
            if "previous_um_knowlege" in request.POST:
                meta_data["previous_um_knowledge"] = request.POST.get("previous_um_knowlege")
            if "english" in request.POST:
                meta_data["english"] = request.POST.get("english")
            if "homework_time" in request.POST:
                meta_data["homework_time"] = request.POST.get("homework_time")
            if "city" in request.POST:
                meta_data["city"] = request.POST.get("city")
            people.meta_data = meta_data
            people.save()

            if "organization" in request.POST and request.POST["organization"]:
                organization = Organization.objects.create(name=request.POST["organization"])

                # Make this person a PlatformU admin, or otherwise a team member of this organization
                relationship = 1 if project.id == 16 else 6
                RecordRelationship.objects.create(
                    record_parent = people,
                    record_child = organization,
                    relationship_id = relationship,
                )

                # And if this is a PlatformU registration, then the organization should be signed
                # up for PlatformU
                if project.id == 16:
                    RecordRelationship.objects.create(
                        record_parent = organization,
                        record_child = project,
                        relationship_id = 27,
                    )

            #Work.objects.create(
            #    name = "Welcome new user",
            #    description = "A new user has signed up for the website! Have a look at their profile, and consider welcoming them. The user has entered the following background information:\n\n" + request.POST.get("background"),
            #    part_of_project = project,
            #    related_to = people,
            #    workactivity_id = 18,
            #    is_public = False,
            #)

            messages.success(request, "You are successfully registered.")

            mailcontext = {
                "name": name,
                "project_name": project.name,
            }

            if "course_signup" in request.GET:
                RecordRelationship.objects.create(
                    record_parent = people,
                    record_child = Course.objects.get(pk=request.GET["course_signup"]),
                    relationship_id = 12,
                )

            if request.project == PROJECT_ID["platformu"]:
                subject = "Welcome to PlatformU"
                msg_html = render_to_string("mailbody/welcome.platformu.html", mailcontext)
                msg_plain = render_to_string("mailbody/welcome.platformu.txt", mailcontext)
            else:
                subject = "Welcome to Metabolism of Cities"
                msg_html = render_to_string("mailbody/welcome.html", mailcontext)
                msg_plain = render_to_string("mailbody/welcome.txt", mailcontext)

            sender = '"' + request.site.name + '" <' + settings.DEFAULT_FROM_EMAIL + '>'
            recipient = '"' + name + '" <' + email + '>'

            if request.project == PROJECT_ID["platformu"]:
                send_mail(
                    subject,
                    msg_plain,
                    sender,
                    [recipient],
                    html_message=msg_html,
                )

            return redirect(redirect_url)

    context = {
        "section": section,
        "menu": "join",
    }
    return render(request, "auth/register.html", context)

def user_login(request, project=None):
    project = get_object_or_404(Project, pk=request.project)
    slug = project.slug if project.slug else "core"
    redirect_url = project.get_website()
    if request.GET.get("next"):
        redirect_url = request.GET.get("next")

    if request.user.is_authenticated:
        return redirect(redirect_url)

    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")
            return redirect(redirect_url)
        else:
            messages.error(request, "We could not authenticate you, please try again.")

    context = {
        "project": project,
        "load_url_fixer": True,
        "reset_link": slug + ":password_reset",
    }
    return render(request, "auth/login.html", context)

def user_logout(request, project=None):
    project = request.project
    logout(request)
    messages.warning(request, "You are now logged out")

    if "next" in request.GET:
        return redirect(request.GET.get("next"))
    elif project:
        info = Project.objects.get(pk=project)
        return redirect(info.get_website())
    else:
        return redirect("core:index")

def user_reset(request):
    return render(request, "auth/reset.html")

def user_profile(request, id=None, project=None):

    if id:
        info = People.objects.get(pk=id)
    elif request.user.is_authenticated:
        info = request.user.people
    else:
        project = get_object_or_404(Project, pk=request.project)
        return redirect(project.get_slug() + ":login")

    completed = Work.objects.filter(assigned_to=info, status=Work.WorkStatus.COMPLETED)
    open = Work.objects.filter(assigned_to=info).filter(Q(status=Work.WorkStatus.OPEN)|Q(status=Work.WorkStatus.PROGRESS))

    context = {
        "menu": "profile",
        "info": info,
        "completed": completed,
        "open": open,
        "load_datatables": True,
    }
    return render(request, "auth/profile.html", context)

@login_required
def user_profile_form(request):
    ModelForm = modelform_factory(
        People,
        fields = ("name", "description", "research_interests", "image", "website", "email", "twitter", "google_scholar", "orcid", "researchgate", "linkedin"),
        labels = { "description": "Profile/bio", "image": "Photo" }
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=request.user.people)
    if request.method == "POST":
        if form.is_valid():
            people = form.save()

            user = people.user
            user.first_name = people.name
            user.username = people.email
            user.email = people.email
            if "password" in request.POST and request.POST["password"]:
                user.set_password(request.POST["password"])
            user.save();

            if "password" in request.POST and request.POST["password"]:
                # user will be logged out after changing password - let's log them back in
                login(request, user)

            meta_data = people.meta_data if people.meta_data else {}
            if "notifications" in request.POST and request.POST["notifications"]:
                meta_data["mute_notifications"] = False
            else:
                meta_data["mute_notifications"] = True
            people.meta_data = meta_data
            people.save()

            messages.success(request, "Your profile information was saved.")
            return redirect(request.GET["return"])
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "menu": "profile",
        "form": form,
        "title": "Edit profile",
    }
    return render(request, "auth/profile.form.html", context)

# Homepage

def index(request):

    count = Project.objects.all().count()
    blurb = """
        <img class="main-logo my-4" alt="Metabolism of Cities" src="/media/logos/Metabolism_of_Cities_full_logo_white.png">
        <div class="my-4 font-weight-bold">
            We are a global network of people working together on systemically
            reducing net environmental impacts of cities
            and territories in a socially just manner and context-specific way. 
        </div>
    """

    alternative_design = False
    if request.user.id == 1 or settings.DEBUG:
        # Paul prefers the homepage in a certain style - different from the actual design
        # because he opens the page many times a day he is hereby creating a setting to 
        # show, only to him, this alternative design
        alternative_design = True
        blurb = """
            <img class="main-logo my-4" alt="Metabolism of Cities" src="/media/logos/Metabolism_of_Cities_full_logo_white.png">
            <div class="row pt-4 my-4 text-center">
              <div class="col-md-4 mb-3">
                <a class="btn btn-lg btn-inverse d-block font-weight-bold py-3" href="forum/">
                  <i class="fa fa-comments-alt"></i> Discuss
                </a>
              </div>
              <div class="col-md-4 mb-3">
                <a class="btn btn-lg btn-inverse d-block font-weight-bold py-3" href="events/">
                  <i class="fa fa-handshake"></i> Get together
                </a>
              </div>
              <div class="col-md-4 mb-3">
                <a class="btn btn-lg btn-inverse d-block font-weight-bold py-3" href="tasks/">
                  <i class="fa fa-hammer"></i> Get things done
                </a>
              </div>
            </div>"""

    context = {
        "HOMEPAGE": True,
        "header_subtitle": blurb,
        "show_project_design": True,
        "projects": Project.objects.filter(pk__in=[2,3,4,32018,16,18]),
        "alternative_design": alternative_design,
        "posts": ForumTopic.objects.order_by("-last_update__date_created")[:3],
        "news": News.objects.filter(projects__in=MOC_PROJECTS).distinct()[:3]
    }
    return render(request, "index.html", context)


# News and events

def news_events_list(request, header_subtitle=None):
    project = get_object_or_404(Project, pk=request.project)
    news = News.objects.filter(projects=project).distinct()
    events = Event.objects.filter(projects=project).distinct()
    context = {
        "news": news,
        "events": events,
        "add_link": "/admin/core/news/add/",
        "header_title": "News and events",
        "header_subtitle": header_subtitle,
        "menu": "news",
    }
    return render(request, "news.events.list.html", context)

def news_list(request, header_subtitle=None):
    if request.project != 1:
        project = get_object_or_404(Project, pk=request.project)
        list = News.objects.filter(projects=project).distinct()
    else:
        list = News.objects.filter(projects__in=MOC_PROJECTS).distinct()
    context = {
        "list": list[3:],
        "shortlist": list[:3],
        "add_link": "/admin/core/news/add/",
        "header_title": "News",
        "header_subtitle": header_subtitle,
        "menu": "news",
    }
    return render(request, "news.list.html", context)

def news(request, slug):
    if request.project != 1:
        project = get_object_or_404(Project, pk=request.project)
        list = News.objects.filter(projects=project)
    else:
        list = News.objects.filter(projects__in=MOC_PROJECTS).distinct()
    info = get_object_or_404(News, slug=slug)
    context = {
        "header_title": "News",
        "header_subtitle": info,
        "info": info,
        "latest": list[:3],
        "edit_link": "/controlpanel/news/" + str(info.id) + "/?next=" + request.get_full_path(),
        "add_link": "/controlpanel/news/create/",
    }
    return render(request, "news.html", context)

def event_list(request, header_subtitle=None):

    article = get_object_or_404(Webpage, pk=47)
    today = timezone.now().date()
    list = Event.objects.filter(end_date__lt=today).order_by("start_date")
    upcoming = Event.objects.filter(end_date__gte=today).order_by("start_date")

    if request.project != 1:
        project = get_object_or_404(Project, pk=request.project)
        # Just un-comment this once all events have been properly tagged
        #list = list.filter(projects=project)
        #upcoming = upcoming.filter(projects=project)

    context = {
        "upcoming": upcoming,
        "archive": list,
        "add_link": "/admin/core/event/add/",
        "header_title": "Events",
        "header_subtitle": "Get involved with the projects at Metabolism of Cities!",
        "sprints": WorkSprint.objects.all(),
        "events": Event.objects.filter(type="training_outreach"),
    }
    return render(request, "event.list.html", context)

def event(request, id, slug):
    info = get_object_or_404(Event, pk=id)
    today = timezone.now().date()
    subscription = None
    participants = None

    if request.user.is_authenticated:
        subscription = RecordRelationship.objects.filter(
            record_parent = request.user.people,
            record_child = info,
            relationship_id = 27,
        )

    if request.user.is_staff:
        participants = RecordRelationship.objects.filter(
            record_child = info,
            relationship_id = 27,
        )

    if "subscribe" in request.POST:
        RecordRelationship.objects.create(
            record_parent = request.user.people,
            record_child = info,
            relationship_id = 27,
        )
        messages.success(request, "You are now registered! You will receive more information by e-mail closer to the date.")
    if "unsubscribe" in request.POST and subscription:
        subscription.delete()
        messages.success(request, "You are no longer registered.")


    context = {
        "info": info,
        "upcoming": Event.objects.filter(end_date__gte=today).order_by("start_date")[:3],
        "header_title": "Events",
        "header_subtitle": info.name,
        "participants": participants,
        "subscription": subscription,

    }
    return render(request, "event.html", context)

# The template section allows contributors to see how some
# commonly used elements are coded, and allows them to copy/paste

def templates(request):
    return render(request, "template/index.html")

def template(request, slug):
    page = "template/" + slug + ".html"

    context = {}
    if slug == "lightbox":
        context["load_lightbox"] = True

    if slug == "address-search":
        from django.conf import settings
        context["geoapify_api"] = settings.GEOAPIFY_API

    if slug == "form":
        ModelForm = modelform_factory(Project, fields=("name", "description"))
        form = ModelForm(request.POST or None, request.FILES or None)
        context["title"] = "Form sample"
        context["form"] = form

    return render (request, page, context)

# The internal projects section

def projects(request):
    article = get_object_or_404(Webpage, pk=PAGE_ID["projects"])
    context = {
        "list": Project.objects.all().exclude(id=1).order_by("name"),
        "article": article,
        "types": ProjectType.objects.all().order_by("name"),
        "header_title": "Projects",
        "header_subtitle": "Overview of projects undertaken by the Metabolism of Cities community",
        "menu": "projects",
    }
    return render(request, "projects.html", context)

def project(request, slug):
    info = get_object_or_404(Project, slug=slug)
    videos = None

    if info.id == 18379:
        # Masterclasses videos
        videos = Video.objects.filter(tags__id=929).order_by("name")
    elif info.slug == "seminarseries":
        videos = Video.objects.filter(tags__id=920).order_by("name")

    context = {
        "edit_link": "/admin/core/project/" + str(info.id) + "/change/",
        "info": info,
        "team": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Team member"),
        "alumni": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Former team member"),
        "partners": Organization.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Partner"),
        "header_title": str(info),
        "header_subtitle_link": "<a style='color:#fff' href='/projects/'>Projects</a>",
        "show_relationship": info.id,
        "menu": "projects",
        "news": News.objects.filter(projects=info).order_by("-date"),
        "videos": videos,
        "events": Event.objects.filter(projects=info).order_by("-start_date"),
    }
    return render(request, "project.html", context)

# Webpage is used for general web pages, and they can be opened in
# various ways (using ID, using slug). They can have different presentational formats

def article(request, id=None, slug=None, prefix=None, project=None, subtitle=None):

    project = request.project

    if id:
        info = get_object_or_404(Webpage, pk=id)
        if info.is_deleted and not request.user.is_staff:
            raise Http404("Webpage not found")
    elif slug:
        if prefix:
            slug = prefix + slug
        slug = slug + "/"
        if project:
            info = Webpage.objects.filter(slug=slug, part_of_project_id=project)
            if not info:
                info = Webpage.objects.filter(slug="/" + slug, part_of_project_id=project)
            info = info[0]
        else:
            info = get_object_or_404(Webpage, slug=slug)

    if not project:
        project = info.part_of_project.id

    context = {
        "info": info,
        "header_title": info.name,
        "header_subtitle": subtitle,
        "webpage": info,
    }
    return render(request, "article.html", context)

def article_list(request, id):
    info = get_object_or_404(Webpage, pk=id)
    list = Webpage.objects.filter(parent=info)
    context = {
        "info": info,
        "list": list,
    }
    return render(request, "article.list.html", context)

# Cities

# Users

def users(request, scoreboard=False):

    webpage = get_object_or_404(Webpage, pk=54)

    if scoreboard:
        page = "scoreboard"
    else:
        page = "users"
    project = None
    if request.project != 1:
        project = request.project
    if "project" in request.GET:
        project = request.GET.get("project")

    list = People.objects.filter(message_list__isnull=False, user__isnull=False).distinct().order_by("-user__date_joined")
    if project:
        list = list.filter(Q(message_list__parent__forumtopic__part_of_project_id=project)|Q(message_list__parent__work__part_of_project_id=project))

    context = {
        "webpage": webpage,
        "list": list,
        "header_title": "Our community",
        "projects": Project.objects.filter(pk__in=OPEN_WORK_PROJECTS),
        "project": int(project) if project else None,
        "load_datatables": True,
        "menu": page,
    }
    return render(request, "contribution/" + page + ".html", context)

def rules(request):

    context = {
        "webpage": get_object_or_404(Webpage, pk=32478),
        "webpage_badges": get_object_or_404(Webpage, pk=32501),
        "menu": "rules",
        "activities": WorkActivity.objects.all(),
        "badges": Badge.objects.all().order_by("code", "type"),
        "header_title": "Our community",
        "header_subtitle": "Points and badges",
        "load_datatables": True,
    }
    return render(request, "contribution/rules.html", context)

# Volunteer hub

def hub(request):
    project = request.project
    if project == 4:
        return work_portal(request, slug="data")
    if project == 17:
        return work_portal(request, slug="data")
    if project == 6:
        return work_portal(request, slug="data")

    updates = Message.objects.filter(
        parent__work__isnull=False,
    ).order_by("-date_created")

    forum = Message.objects.filter(
        parent__forumtopic__isnull=False,
        parent__forumtopic__parent_id=31993,
    ).order_by("-date_created")

    master_list = False
    if not master_list:
        updates = updates.filter(parent__work__part_of_project_id=project)
        forum = forum.filter(parent__forumtopic__part_of_project_id=project)

    context = {
        "updates": updates[:7] if updates else None,
        "menu": "home",
        "forum": forum[:7] if forum else None,
    }
    return render(request, "hub/index.html", context)

def hub_latest(request, network_wide=False):
    project = request.project
    days = 7
    from datetime import datetime, timedelta
    generate_date = datetime.now() - timedelta(days=days)

    if request.GET.get("days"):
        days = request.GET.get("days")


    if network_wide:
        # The network-wide update page shows updates from ALL the projects,
        # plus it shows both task updates (work) and forum updates (forumtopic)
        updates = Message.objects.filter(
            date_created__gte=generate_date,
        )
        updates = updates.filter(Q(parent__work__isnull=False)|Q(parent__forumtopic__isnull=False)).order_by("-date_created")
        menu = "network_log"
    else:
        updates = Message.objects.filter(
            date_created__gte=generate_date,
            parent__work__isnull=False,
            parent__work__part_of_project_id=project
        ).order_by("-date_created")
        menu = "log"

    context = {
        "updates": updates,
        "load_datatables": True,
        "menu": menu,
        "days": int(days),
    }
    return render(request, "hub/latest.html", context)

def hub_help(request):
    project = request.project
    context = {
        "menu": "help",
        "webpage": Webpage.objects.get(pk=31997),
    }
    return render(request, "hub/help.html", context)

def hub_selector(request):
    project = request.project
    context = {
        "menu": "help",
    }
    return render(request, "hub/selector.html", context)

# Control panel and general contribution components

@login_required
def controlpanel(request, space=None):

    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    if space:
        space = get_space(request, space)

    context = {
        "space": space,
        "title": "Control panel",
    }
    return render(request, "controlpanel/index.html", context)

@login_required
def controlpanel_users(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)
    context = {
        "users": RecordRelationship.objects.filter(record_child_id=request.project),
        "load_datatables": True,
    }
    return render(request, "controlpanel/users.html", context)

@login_required
def controlpanel_relationship_form(request, id=None):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = None
    child = None

    if id:
        info = RecordRelationship.objects.get(pk=id)

    if not child:
        child = get_object_or_404(Project, pk=request.project)        

    if request.method == "POST":
        if not id:
            info = RecordRelationship()
        info.record_parent_id = request.POST.get("record_parent")
        info.record_child = child
        info.relationship_id = request.POST.get("relationship")
        info.save()
        if "date" in request.POST:
            info.date_created = request.POST.get("date")
            info.save()
        messages.success(request, "The information was saved.")
        if "next" in request.GET:
            return redirect(request.GET.get("next"))

    context = {
        "type": "people",
        "load_select2": True,
        "relationships": Relationship.objects.filter(pk__in=[7,6]),
        "child": child,
        "info": info,
    }
    return render(request, "controlpanel/relationship.html", context)

@login_required
def controlpanel_design(request):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = ProjectDesign.objects.get(pk=project)
    ModelForm = modelform_factory(
        ProjectDesign,
        fields = ("header", "logo", "header_color", "custom_css", "back_link"),
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            messages.success(request, "The new design was saved")

    context = {
        "form": form,
        "header_title": "Design",
        "header_subtitle": "Use this section to manage the design of this site",
    }
    return render(request, "controlpanel/design.html", context)

@login_required
def controlpanel_design(request):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = ProjectDesign.objects.get(pk=project)
    ModelForm = modelform_factory(
        ProjectDesign,
        fields = ("header", "logo", "header_color", "custom_css", "back_link"),
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            messages.success(request, "The new design was saved")

    context = {
        "form": form,
        "header_title": "Design",
        "header_subtitle": "Use this section to manage the design of this site",
    }
    return render(request, "controlpanel/design.html", context)

@login_required
def controlpanel_project(request):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = Project.objects.get(pk=project)
    ModelForm = modelform_factory(
        Project,
        fields = ("name", "description", "type", "start_date", "end_date", "screenshot", "summary_sentence"),
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            messages.success(request, "Project details were saved")

    context = {
        "form": form,
        "header_title": "Project settings",
        "header_subtitle": "Use this section to manage the general project details",
    }
    return render(request, "controlpanel/project.html", context)

@login_required
def controlpanel_news(request):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    list = News.objects.all()
    if request.project != 1:
        list = list.filter(projects__id=project)

    context = {
        "pages": list,
        "load_datatables": True,
        "title": "News",
    }
    return render(request, "controlpanel/news.html", context)

@login_required
def controlpanel_news_form(request, id=None):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = None
    ModelForm = modelform_factory(News, fields=("name", "date", "image", "projects", "include_in_timeline", "is_deleted"))
    if id:
        info = get_object_or_404(News, pk=id)
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    else:
        form = ModelForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            if not id:
                info.part_of_project_id = project
            info.description = request.POST.get("description")
            meta_data = info.meta_data if info.meta_data else {}
            meta_data["format"] = request.POST.get("format")
            info.meta_data = meta_data
            info.save()
            form.save_m2m()

            # TO DO
            # There is a contraint, for slug + project combined, and we should
            # check for that and properly return an error

            existing_authors = []
            if info.authors:
                for each in info.authors():
                    existing_authors.append(each.id)

            if "authors" in request.POST:
                for each in request.POST.getlist("authors"):
                    each = int(each)
                    if each not in existing_authors:
                        RecordRelationship.objects.create(
                            record_parent_id = each,
                            record_child = info,
                            relationship_id = 4,
                        )
                    else:
                        existing_authors.remove(each)

            for each in existing_authors:
                check = RecordRelationship.objects.filter(record_parent_id=each, record_child=info, relationship_id=4)
                check.delete()

            messages.success(request, "Information was saved.")
            url = info.get_absolute_url()
            messages.warning(request, f'<a href="{url}"><i class="fa fa-fw fa-link"></i> View news article</a>')
            if "next" in request.GET:
                return redirect(request.GET.get("next"))
            else:
                return redirect("../")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "load_select2": True,
        "form": form,
        "info": info,
        "title": info.name if info else "Create news article",
        "load_markdown": True,
    }
    return render(request, "controlpanel/news.form.html", context)

@login_required
def controlpanel_content(request):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    context = {
        "pages": Webpage.objects.filter(part_of_project_id=project),
        "load_datatables": True,
        "title": "Web page content",
    }
    return render(request, "controlpanel/content.html", context)

@login_required
def controlpanel_content_form(request, id=None):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = None
    ModelForm = modelform_factory(Webpage, fields=("name", "slug", "is_deleted"))
    if id:
        info = get_object_or_404(Webpage, pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            if not id:
                info.part_of_project_id = project
            info.description = request.POST.get("description")
            meta_data = info.meta_data if info.meta_data else {}
            meta_data["format"] = request.POST.get("format")
            info.meta_data = meta_data
            info.save()
            # TO DO
            # There is a contraint, for slug + project combined, and we should
            # check for that and properly return an error
            messages.success(request, "Information was saved.")
            return redirect(request.GET.get("next"))
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "pages": Webpage.objects.filter(part_of_project_id=project),
        "load_datatables": True,
        "form": form,
        "info": info,
        "title": info.name if info else "Create webpage",
        "load_markdown": True,
    }
    return render(request, "controlpanel/content.form.html", context)

@login_required
def controlpanel_cache(request):

    from django.core.cache import caches, cache

    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    list = caches
    if request.method == "POST" and "delete" in request.POST:
        cache.clear()
        messages.success(request, "All cache was cleared.")

    context = {
        "title": "Control panel",
    }
    return render(request, "controlpanel/cache.html", context)


@login_required
def controlpanel_data_articles(request, space):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    space = get_space(request, space)
    context = {
        "list": DataArticle.objects.filter(part_of_project_id=project, spaces=space),
        "load_datatables": True,
        "space": space,
    }
    return render(request, "controlpanel/data-articles.html", context)

@login_required
def controlpanel_data_article(request, space, id=None):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    space = get_space(request, space)
    ModelForm = modelform_factory(
        DataArticle,
        fields=("name", "category", "sub_category", "completion"),
        labels = { "name": "Title", "sub_category": "Sub category (optional)" },
    )
    info = get_object_or_404(DataArticle, pk=id, part_of_project_id=project) if id else None
    form = ModelForm(request.POST or None, instance=info)
    if request.method == 'POST':
        if form.is_valid():
            info = form.save(commit=False)
            info.part_of_project_id = project
            info.description = request.POST.get("text")
            info.save()
            if not id:
                info.spaces.add(space)
            messages.success(request, "The data article was added.")
            return redirect("data:controlpanel_data_articles", space=space.slug)
        else:
            messages.error(request, 'We could not save your form, please fill out all fields')

    context = {
        "articles": DataArticle.objects.filter(part_of_project_id=project, spaces=space),
        "load_datatables": True,
        "space": space,
        "form": form,
        "info": info,
    }
    return render(request, "controlpanel/data-article.html", context)

@login_required
def work_form(request, id=None, sprint=None):
    project = request.project
    info = None
    fields = ["name", "priority", "workactivity", "url"]
    if request.user.is_staff:
        fields += ["part_of_project"]
    if request.user.is_authenticated and has_permission(request, request.project, ["admin", "team_member"]):
        fields += ["is_public", "tags"]
    ModelForm = modelform_factory(Work, fields=fields, labels={"url": "URL", "workactivity": "Type of activity"})
    if id and request.user.is_authenticated and has_permission(request, request.project, ["admin", "team_member"]):
        info = Work.objects_include_private.get(pk=id)
        form = ModelForm(request.POST or None, instance=info)
    elif id:
        # Needs improvement
        info = Work.objects_include_private.get(pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None, initial={"part_of_project": project})
    if "tags" in fields:
        form.fields["tags"].queryset = Tag.objects.filter(parent_tag_id=809)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.description = request.POST["description"]

            if not id:
                info.status = Work.WorkStatus.OPEN
                info.part_of_project_id = project

            info.save()
            form.save_m2m()

            if not id:
                message = Message.objects.create(
                    name = "Task created",
                    description = "New task was created",
                    parent = info,
                    posted_by = request.user.people,
                )
                set_autor(request.user.people.id, message.id)
                info.subscribers.add(request.user.people)

            if request.FILES:
                files = request.FILES.getlist("files")
                for file in files:
                    attachment = Document()
                    filename = str(file)
                    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                        attachment.image = file
                    else:
                        attachment.file = file
                    attachment.name = file
                    attachment.save()
                    message.attachments.add(attachment)


            messages.success(request, "Information was saved.")
            return redirect(request.GET["return"])
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "title": "Create new task" if not id else info.name,
        "form": form,
        "load_markdown": True,
        "load_select2": True,
        "info": info,
        "menu": "work",
        "header_title": "Tasks",
        "header_subtitle": "Let's build things together, one item at a time!",
    }
    return render(request, "contribution/work.form.html", context)

def work_grid(request, sprint=None):

    project = request.project
    status = request.GET.get("status")
    type = request.GET.get("type")
    priority = request.GET.get("priority")
    selected_project = None

    if request.user.is_authenticated and has_permission(request, request.project, ["admin", "team_member"]):
        list = Work.objects_include_private.all()
    else:
        list = Work.objects.all()

    if "entry" in request.GET:
        list = list.filter(tags=810)

    if sprint:
        sprint = WorkSprint.objects.get(pk=sprint)
        list = list.filter(part_of_project__in=sprint.projects.all())
    elif "project" in request.GET and request.GET["project"]:
        selected_project = request.GET.get("project")
        list = list.filter(part_of_project_id=selected_project)
    elif project != 1:
        list = list.filter(part_of_project_id=project)
        selected_project = project

    if "tag" in request.GET and request.GET["tag"]:
        list = list.filter(tags=get_object_or_404(Tag, pk=request.GET["tag"]))

    if "bot_hide" in request.GET and request.GET["bot_hide"]:
        list = list.exclude(last_update__posted_by_id=32070)

    if status:
        if status == "open_unassigned":
            list = list.filter(status=1, assigned_to__isnull=True)
        else:
            list = list.filter(status=status)
            status = int(status)

    if priority:
        list = list.filter(priority=priority)

    if type:
        list = list.filter(workactivity__type=type)

    list = list.order_by("-last_update__date_created")
    projects = Project.objects.filter(pk__in=OPEN_WORK_PROJECTS).order_by("name")

    if list.count() > 200:
        list = list[:200]
        messages.warning(request, "There are more than 200 tasks found. We only show the first 200 tasks. Use the filters to find the right tasks.")

    context = {
        "task_list": list,
        "load_datatables": True,
        "statuses": Work.WorkStatus.choices,
        "priorities": Work.WorkPriority.choices,
        "title": "Work grid",
        "types": WorkActivity.WorkType,
        "status": status,
        "type": int(type) if type else None,
        "priority": int(priority) if priority else None,
        "sprint": sprint,
        "menu": "work",
        "projects": projects,
        "selected_project": int(selected_project) if selected_project else None,
        "header_title": "Tasks",
        "header_subtitle": "Let's build things together, one item at a time!",
    }
    return render(request, "contribution/work.grid.html", context)

def work_item(request, id, sprint=None):
    # To do: validate user has access to this ticket
    # if at all needed?
    if request.user.is_authenticated and has_permission(request, request.project, ["admin", "team_member"]):
        info = Work.objects_include_private.get(pk=id)
    else:
        info = Work.objects.get(pk=id)

    if sprint:
        sprint = WorkSprint.objects.get(pk=sprint)
    else:
        # Check if there are active sprints and if this is part of that sprint
        sprints = WorkSprint.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now())
        if sprints:
            check_sprint = sprints[0]
            if check_sprint.work_tag in info.tags.all():
                sprint = check_sprint


    message_list = Message.objects.filter(parent=info)
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(people=request.user.people, record__in=message_list, is_read=False)
        notifications.update(is_read=True)

    if request.method == "POST":

        message_title = message_description = None

        if "assign_to_me" in request.POST:
            if info.assigned_to:
                messages.warning(request, "Sorry, this task was assigned to someone else just now!")
            else:
                message_title = "Task assigned"
                message_description = "Task was assigned to " + str(request.user.people)
                message_success = "This task is now assigned to you"
                info.assigned_to = request.user.people
                info.subscribers.add(request.user.people)
                info.save()

        if "status_change" in request.POST and info.status != request.POST["status_change"]:
            message_description = "Status change: " + info.get_status_display() + " → "
            info.status = request.POST.get("status_change")
            info.save()
            info.refresh_from_db()
            new_status = str(info.get_status_display())
            message_description += new_status
            message_title = "Status change"
            message_success = "Task status change was recorded"

        if "unassign" in request.POST:
            info.assigned_to = None
            info.save()
            message_description = str(request.user.people) + " is no longer responsible for this task"
            message_title = "Task unassigned"
            message_success = "You are no longer responsible for this task"

        if "subscribe" in request.POST:
            info.subscribers.add(request.user.people)
            messages.success(request, "You will now receive notifications!")

        if "unsubscribe" in request.POST:
            info.subscribers.remove(request.user.people)
            messages.success(request, "You will no longer receive notifications!")

        if message_title and message_description:
            message = Message.objects.create(
                name = message_title,
                description = message_description,
                parent = info,
                posted_by = request.user.people,
            )
            set_autor(request.user.people.id, message.id)
            messages.success(request, message_success)

            for each in info.subscribers.all():
                if each.people != request.user.people:
                    Notification.objects.create(record=message, people=each.people)

            if info.get_status_display() == "In Progress" and info.url:
                return redirect(info.url)

    context = {
        "info": info,
        "load_messaging": True,
        "list_messages": message_list,
        "forum_title": "History and discussion",
        "title": info.name,
        "sprint": sprint,
        "menu": "work",
        "header_title": "Tasks",
        "header_subtitle": "Let's build things together, one item at a time!",
    }

    if request.user.is_authenticated and not request.user.people in info.subscribers.all():
        context["show_subscribe"] = True

    return render(request, "contribution/work.item.html", context)

def work_sprints(request):
    project = request.project
    list = WorkSprint.objects.filter(projects__id=project)
    context = {
        "add_link": "/admin/core/worksprint/add/",
        "list": list,
        "article": get_object_or_404(Webpage, pk=18965)
    }
    return render(request, "contribution/work.sprints.html", context)

def work_sprint(request, id=None):

    project = get_object_or_404(Project, pk=request.project)
    info = WorkSprint.objects.get(pk=id)
    updates = None
    last_update = 0
    if request.method == "POST":
        if "sign_me_up" in request.POST:
            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child = info,
                relationship_id = 27,
            )
            messages.success(request, "Great! You are now signed up for this sprint.")
    if info.end_date:
        updates = Message.objects.filter(
            date_created__gte=info.start_date,
            date_created__lte=info.end_date,
            parent__work__part_of_project__in=info.projects.all(),
        ).order_by("date_created")
        if updates:
            last_update = updates[len(updates)-1].id
        if "updates_since" in request.GET:
            updates = updates.filter(id__gt=request.GET["updates_since"]).exclude(posted_by=request.user.people)
            return JsonResponse({"updates":updates.count()})

    message_list = Chat.objects.filter(channel=id).order_by("timestamp")

    work_list = {}
    if info.work_tag:
        work_all = Work.objects.filter(tags=info.work_tag)
        updates = updates.order_by("-date_created")
        work_list = {
            "all": work_all.count(),
            "unassigned": work_all.filter(assigned_to__isnull=True).count(),
            "done": work_all.filter(status=Work.WorkStatus.COMPLETED).count(),
            "progress": work_all.filter(status=Work.WorkStatus.PROGRESS).count(),
            "percentage": work_all.filter(status=Work.WorkStatus.COMPLETED).count()/work_all.count()*100 if work_all else 0,
            "my_work": work_all.filter(assigned_to=request.user.people) if request.user.is_authenticated else None,
        }
        updates = updates.filter(parent__work__tags=info.work_tag)

    context = {
        "info": info,
        "edit_link": "/admin/core/worksprint/" + str(info.id) + "/change/",
        "title": info,
        "updates": updates,
        "last_update": last_update,
        "message_list": message_list,
        "participants": People.objects.filter(parent_list__record_child=info, parent_list__relationship__id=27),
        "work_list": work_list,
        "task_url": project.get_slug() + ":work_sprint_tasks",
    }

    return render(request, "contribution/work.sprint.html", context)

def work_portal(request, slug, space=None):

    if space:
        space = get_space(request, space)

    project = get_object_or_404(Project, pk=request.project)
    pages = {
        "data": 32985,
        "islands": 32985,
        "design": 32969
    }

    tasks = None

    if slug == "design":

        if request.user.is_authenticated and has_permission(request, request.project, ["admin", "team_member"]):
            tasks = Work.objects_include_private.all()
        else:
            tasks = Work.objects.all()

        tasks = tasks.filter(workactivity__type=WorkActivity.WorkType.DESIGN)

    info = get_object_or_404(Webpage, pk=pages[slug])
    context = {
        "webpage": info,
        "slug": slug,
        "load_messaging": True,
        "show_subscribe": True,
        "info": info,
        "list_messages": Message.objects.filter(parent=info),
        "task_list": tasks.order_by("-last_update") if tasks else None,
        "menu": "home",
        "space": space,
        "hide_space_menu": True,
    }

    if slug == "data":
        context["layers"] = Tag.objects.filter(parent_tag_id=845)
        context["spaces"] = ActivatedSpace.objects.filter(part_of_project_id=request.project)
        context["datalink"] = project.slug + ":hub_harvesting_space"

    return render(request, "contribution/portal.html", context)


@login_required
def notifications(request):

    if "read" in request.POST:
        read = request.POST.get("read")
        items = read.split(",")
        # The last item is always empty as we create the string like 40, 302, 23,
        del items[-1]
        delete_list = Notification.objects.filter(people=request.user.people, pk__in=items)
        delete_list.update(is_read=True)
        messages.success(request, "Your notifications were marked as read!")

    list = Notification.objects.filter(people=request.user.people, is_read=False)
    unread = True

    if not list:
        old = Notification.objects.filter(people=request.user.people, is_read=True).order_by("-id")
        if old:
            list = old[:15]
            unread = False

    context = {
        "list": list,
        "title": "Notifications",
        "unread": unread,
    }
    return render(request, "contribution/notifications.html", context)

# Social media

@staff_member_required
def socialmedia(request):
    list = SocialMedia.objects.exclude(status="discarded")
    if "campaign" in request.GET and request.GET["campaign"]:
        list = list.filter(campaign_id=request.GET.get("campaign"))
    context = {
        "list": list,
        "menu": "content",
        "load_datatables": True,
    }
    return render(request, "socialmedia/index.html", context)

@staff_member_required
def socialmedia_campaigns(request):
    list = Tag.objects.filter(parent_tag=927)
    context = {
        "list": list,
        "menu": "campaigns",
    }
    return render(request, "socialmedia/campaigns.html", context)

@staff_member_required
def socialmedia_campaign(request, id=None):
    ModelForm = modelform_factory(Tag, fields=["name", "description", "color"])

    if id:
        info = get_object_or_404(Tag, pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.parent_tag_id = 927
            info.save()

            messages.success(request, "Campaign was saved.")
            return redirect(reverse("core:socialmedia_campaigns"))
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "form": form,
        "title": "Social media campaign",
        "menu": "campaigns",
    }
    return render(request, "socialmedia/campaign.html", context)

@staff_member_required
def socialmedia_form(request, id=None):

    ModelForm = modelform_factory(SocialMedia, fields=["name", "description", "image", "campaign", "status", "date", "platforms"])
    record = None

    if id:
        info = get_object_or_404(SocialMedia, pk=id)
        record = info
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    elif "record" in request.GET:
        record = get_object_or_404(Record, pk=request.GET["record"])
        # Remove tags
        if record.description:
            description = re.sub('<[^<]+?>', '', record.description)
        else:
            description = None
        form = ModelForm(request.POST or None, initial={"name": record.name, "description": description, "image": record.image})
    else:
        form = ModelForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            if "record" in request.GET:
                info.record = record
            info.save()
            form.save_m2m()

            messages.success(request, "Post was saved.")
            return redirect(reverse("core:socialmedia"))
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "list": list,
        "form": form,
        "record": record,
        "title": "Load new post",
        "menu": "content",
    }
    return render(request, "socialmedia/form.html", context)

@staff_member_required
def socialmedia_form_search(request):
    context = {
        "load_select2": True,
        "menu": "content",
    }
    return render(request, "socialmedia/search.html", context)

@staff_member_required
def search_ajax(request, type):
    query = request.GET.get("q")
    r = {
        "results": []
    }
    if query:
        if type == "news":
            list = News.objects.all()
        elif type == "event":
            list = Event.objects.all()
        elif type == "project":
            list = Project.objects.all()
        elif type == "dataset":
            list = Dataset.objects.all()
        elif type == "video":
            list = Video.objects.all()
        elif type == "course":
            list = Course.objects.all()
        elif type == "people":
            list = People.objects.all()

        list = list.filter(name__icontains=query)
        for each in list:
            r["results"].append({"id": each.id, "text": each.name})
    return JsonResponse(r, safe=False)

# People

def contributor(request):
    project = get_object_or_404(Project, pk=request.project)
    if request.method == "POST":
        Work.objects.create(
            name = "Process collaborator signup form: " + request.POST.get("name"),
            status = Work.WorkStatus.OPEN,
            priority = Work.WorkPriority.HIGH,
            part_of_project = project,
            workactivity_id = 16,
            meta_data = request.POST,
        )
        messages.success(request, "Thanks! Our team will be in touch with you soon.")
    context = {
        "info": project,
        "title": "Contributor page",
    }
    return render(request, "contribution/contributor.page.html", context)

def support(request):
    project = get_object_or_404(Project, pk=request.project)
    if request.method == "POST":
        Work.objects.create(
            name = "Process collaborator signup form: " + request.POST.get("name"),
            status = Work.WorkStatus.OPEN,
            priority = Work.WorkPriority.HIGH,
            part_of_project = project,
            workactivity_id = 16,
            meta_data = request.POST,
        )
        messages.success(request, "Thanks! Our team will be in touch with you soon.")
    context = {
        "info": project,
        "title": "Contributor page",
    }
    return render(request, "contribution/contributor.page.html", context)

def newsletter(request):
    is_subscribed = None
    if request.user.is_authenticated:
        is_subscribed = RecordRelationship.objects.filter(relationship_id=28, record_parent=request.user.people, record_child_id=request.project)

    if request.method == "POST":

        if "unsubscribe" in request.POST and is_subscribed:
            is_subscribed.delete()
            messages.success(request, "You have successfully unsubscribed.")
        elif not is_subscribed:
            if request.user.is_authenticated:
                people = request.user.people
            else:
                people = People.objects.create(
                    name = request.POST.get("name"),
                    email = request.POST.get("email"),
                )
            RecordRelationship.objects.create(
                relationship_id = 28,
                record_parent = people,
                record_child_id = request.project,
            )
            is_subscribed = True
            messages.success(request, "You have successfully subscribed to our newsletter")

    context = {
        "title": "Newsletter signup",
        "is_subscribed": is_subscribed,
    }
    return render(request, "newsletter.html", context)


# TEMPORARY PAGES DURING DEVELOPMENT

def pdf(request):
    name = request.GET["name"]
    score = request.GET["score"]
    date = datetime.now()
    date = date.strftime("%d %B %Y")
    site = Site.objects.get_current()

    context = Context({"name": name, "score": score, "date": date, "site": site.domain})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=test.pdf"
    html = render_to_string("pdf_template.html", context.flatten())

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)

    return response

def socialmedia_post(request, type):
    list = SocialMedia.objects.filter(published=False, platform=type)
    response = ""
    for each in list:
        # send to api here
        success = False
        if type == "facebook":
            fb_access_token = settings.FACEBOOK_ACCESS_TOKEN
            graph = facebook.GraphAPI(access_token=fb_access_token, version="2.12")
            message = each.blurb
            try:
                graph.put_object(parent_object="me", connection_name="feed", message=message)
                success = True
            except Exception as e:
                response = e
        elif type == "twitter":
            access_token = settings.TWITTER_API_ACCESS_TOKEN
            access_token_secret = settings.TWITTER_API_ACCESS_TOKEN_SECRET
            consumer_key = settings.TWITTER_API_CONSUMER_KEY
            consumer_secret = settings.TWITTER_API_CONSUMER_SECRET
            api = twitter.Api(consumer_key, consumer_secret, access_token, access_token_secret)
            message = each.blurb
            response = None
            try:
                api.PostUpdate(message)
                success = True
            except Exception as e:
                response = e
        elif type == "linkedin":
            import requests

            message = each.blurb

            #LINKEDIN_API_ACCESS_TOKEN = "AQWK3cfYBPf7GsNQr1-PG1NXGZsKcVCLoNVz8o7j1e1U7LvZAQ6oLk4aZRp9ChHQpzvXqdiwMoU7cNDTUb6SWWjprePCW16NsJtvRGPzzqoyc3JSN1g_x9Vr1UgNMeyca97kaKYrFkdNHnXITCsveRTSiE33UXJPJcXu_caV0m_BBhRuVCXDfBPT3BH_Zu12IXpf9n8I7pJWC790ZVJo1TWmV_UUPNHpIFiyqIQnXwuKpIJjDI2v7l0tTqE9hBuGyDBvEhBzylCc___njboDxc-xQUYK8bjdM7qfcDrA13dZgoad3DrXHcdHU5MoG4d74enfw4RgzMEQQlg4isoEggJsdAxfsg"
            LINKEDIN_API_ACCESS_TOKEN = "AQUZt-OcxMf3AxkRgeIYAaNkhEWGUZAHoSutRZJb8gby4Y74Y5R0uXdST54-8jLxRU1kOs1u1wD2CAniiiVe1ZD9s11uRWQvW3GN9Afg8uagyPMXAjsAI3tYK-MXIy5d-W51VZom0tiZfPFifinLk1GZLoJhIPxdtyoUQp_jZwpaz5sQjsZq8IR-XbNZj2tj5G_fCSfBHAY32CPYsjcWxzdPnYg4uL-4s-tfWtNz7rQHcvGcUyKO_mtCsak2ZFxwmXMxQwpS4T9IBE5p4nUXyIX6JjVysYT6GIWsapbYSKr3ab_H2QuC9BtmWVMv4OGDZnygB0dAcNac98-vAZRoKsDrsbI2LQ"
            access_token = LINKEDIN_API_ACCESS_TOKEN
            urn = "icHtLHqHA7"
            author = f"urn:li:person:{urn}"

            api_url = "https://api.linkedin.com/v2/ugcPosts"

            headers = {
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json",
                "Connection": "Keep-Alive",
                "Authorization": f"Bearer {access_token}",
            }

            post_data = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": message
                        },
                        "shareMediaCategory": "NONE"
                    },
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"
                },
            }

            response = requests.post(api_url, headers=headers, json=post_data)

            if response.status_code == 201:
                print("Success")
                print(response.content)

                success = True
            else:
                print(response.content)

            response = response.content

        elif type == "instagram":
            message = each.blurb
            # In Instagram we need of course to post an image, so please use this as well:
            image = each.record.image
            response = "response-from-api"
        if success:
            each.published = True
        each.response = response
        each.save()

    context = {
        "response": response,
    }

    messages.success(request, "Messages were posted.")
    return render(request, "template/socialmedia.html", context)

def socialmediaCallback(request, type):
    context = {
        "callback": request
    }

    return render(request, "template/callback.html", context)
#MOOC

def mooc(request, id):
    mooc = get_object_or_404(MOOC, pk=id)
    modules = mooc.modules.all().order_by("id")

    context = {
        "mooc": mooc,
        "modules": modules,
    }

    return render(request, "mooc/index.html", context)

def mooc_module(request, id, module):
    mooc = get_object_or_404(MOOC, pk=id)
    module = get_object_or_404(MOOCModule, pk=module)
    questions = module.questions.all()

    context = {
        "mooc": mooc,
        "module": module,
        "questions": questions,
    }

    return render(request, "mooc/module.html", context)

# Temp stuff

@login_required
def tags(request):
    list = Tag.objects_unfiltered.all()
    context = {
        "list": list,
        "load_datatables": True,
    }
    return render(request, "temp.tags.html", context)


def load_baseline(request):

    return redirect("/")

def project_form(request):
    ModelForm = modelform_factory(Project, fields=("name", "content", "email", "url", "image"))
    form = ModelForm(request.POST or None, request.FILES or None)
    is_saved = False
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.is_deleted = True
            info.save()
            info_id = info.id
            messages.success(request, "Information was saved.")
            is_saved = True
            name = request.POST["name"]
            user_email = request.POST["user_email"]
            posted_by = request.POST["name"]
            host_name = request.get_host()
            review_link = f"{host_name}/admin/core/project/{info_id}/change/"
            send_mail(
                "New project created",
f'''A new project was created, please review:

Project name: {name}
Submitted by: {posted_by}
Email: {user_email}

Link to review: {review_link}''',
                user_email,
                ["info@metabolismofcities.org"],
                fail_silently=False,
            )
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "form": form,
        "is_saved": is_saved
    }
    return render(request, "project.form.html", context)

@login_required
def massmail(request,people=None):
    try:
        id_list = request.GET["people"]
        last_char = id_list[-1]
        if last_char == ",":
            id_list = id_list[:-1]
        ids = id_list.split(",")
        list = People.objects.filter(id__in=ids)
    except Exception as e:
        messages.error(request, "You did not select any people to send this mail to! <br><strong>Error: " + str(e) + "</strong>")
        list = None
    if request.method == "POST":
        try:
            message = request.POST["content"]
            mailcontext = {
                "message": markdown(message),
            }
            msg_html = render_to_string("mailbody/mail.template.html", mailcontext)
            msg_plain = message
            sender = '"' + request.site.name + '" <' + settings.DEFAULT_FROM_EMAIL + '>'
            if "send_preview" in request.POST:
                # If a preview is being sent, then it must ONLY go to the logged-in user
                recipients = People.objects.filter(user=request.user)
            else:
                recipients = list
            for each in recipients:
                # Let check if the person has an email address before we send the mail
                if each.email:
                    recipient = '"' + each.name + '" <' + each.email + '>'
                    send_mail(
                        request.POST["subject"],
                        msg_plain,
                        sender,
                        [recipient],
                        html_message=msg_html,
                    )
            messages.success(request, "The message was sent.")
        except Exception as e:
            messages.error(request, "We could not send your mail, please review the error.<br><strong>" + str(e) + "</strong>")

    context = {
        "list": list,
        "load_markdown": True,
    }
    return render(request, "massmail.html", context)

# TEMPORARY
def dataimport(request):
    error = False
    return redirect("/")
    if "table" in request.GET:
        messages.warning(request, "Trying to import " + request.GET["table"])
        file = settings.MEDIA_ROOT + "/import/" + request.GET["table"] + ".csv"
        messages.warning(request, "Using file: " + file)
        if request.GET["table"] == "activities":
            ActivityCatalog.objects.all().delete()
            nace = ActivityCatalog.objects.create(name="Statistical Classification of Economic Activities in the European Community, Rev. 2 (2008)", url="https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=NACE_REV2&StrLanguageCode=EN&IntPcKey=&StrLayoutCode=HIERARCHIC")
            natural = ActivityCatalog.objects.create(name="Rupertismo List of Natural Processes")
            Activity.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    id = int(row["id"])
                    catalog = None
                    if id > 398480:
                        catalog = nace
                    elif id > 65 and id < 95 and id != 92:
                        catalog = natural
                    if catalog:
                        Activity.objects.create(
                            old_id = row["id"],
                            name = row["name"],
                            description = row["description"],
                            is_separator = row["is_separator"],
                            code = row["code"],
                            catalog = catalog,
                        )
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    id = int(row["id"])
                    parent = None
                    if id > 398480:
                        if int(row["parent_id"]) == 398480:
                            parent = None
                        else:
                            parent = Activity.objects.get(old_id=row["parent_id"])
                    elif id > 65 and id < 95 and id != 92:
                        if int(row["parent_id"]) == 92:
                            parent = None
                        else:
                            parent = Activity.objects.get(old_id=row["parent_id"])
                    if parent:
                        info = Activity.objects.get(old_id=row["id"])
                        info.parent = parent
                        info.save()
        elif request.GET["table"] == "libraryspaces":
            list = LibraryItem.objects.all()
            for each in list:
                each.spaces.clear()
            spaces = {}
            items = {}
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if row["referencespace_id"] in spaces:
                        space = spaces[row["referencespace_id"]]
                    else:
                        space = ReferenceSpace.objects.filter(old_id=row["referencespace_id"])
                        if space:
                            space = space[0]
                        else:
                            print("COULD NOT FIND THIS!!")
                            print(row)
                        spaces[row["referencespace_id"]] = space
                    if row["reference_id"] in items:
                        item = items[row["reference_id"]]
                    else:
                        item = LibraryItem.objects.filter(old_id=row["reference_id"]).exclude(type__name="Video Recording").exclude(type__name="Image")
                        if item.count() == 1:
                            item = item[0]
                        else:
                            print("Duplication error!")
                            print(item)
                        items[row["reference_id"]] = item
                    if space:
                        item.spaces.add(space)
        elif request.GET["table"] == "sectors":
            Sector.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    Sector.objects.create(
                        old_id = row["id"],
                        name = row["name"],
                        icon = row["icon"],
                        slug = row["slug"],
                        description = row["description"],
                    )
        elif request.GET["table"] == "sectoractivities":
            sectors = Sector.objects.all()
            for each in sectors:
                each.activities.clear()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                sectors = {}
                for row in contents:
                    row["processgroup_id"] = int(row["processgroup_id"])
                    if row["processgroup_id"] not in sectors:
                        sectors[row["processgroup_id"]] = Sector.objects.get(old_id=row["processgroup_id"])
                    sector = sectors[row["processgroup_id"]]
                    sector.activities.add(Activity.objects.get(old_id=row["process_id"]))
        elif request.GET["table"] == "spacesectors":
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    space = ReferenceSpace.objects.get(old_id=row["space_id"])
                    sector = Sector.objects.get(old_id=row["process_group_id"])
                    space.sectors.add(sector)
        elif request.GET["table"] == "photos":
            Photo.objects_unfiltered.all().delete()
            list = User.objects.all()
            for each in list:
                checkpeople = People.objects.filter(user=each)
                if checkpeople:
                    print("YES!!")
                else:
                    check = People.objects.filter(email=each.email)
                    if check:
                        try:
                            print("WE FOUND A MATCH!!!!!!")
                            p = check[0]
                            p.user = each
                            p.save()
                        except:
                            print("FAIL _------_--")
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                from dateutil.parser import parse
                for row in contents:
                    deadline = parse(row["created_at"])
                    year = deadline.strftime("%Y")
                    info = Photo.objects.create(
                        name = row["description"][:255],
                        description = row["description"] if len(row["description"]) > 255 else None,
                        image = row["image"],
                        is_deleted = row["deleted"],
                        license_id = row["license_id"],
                        type = LibraryItemType.objects.get(name="Image"),
                        position = row["position"],
                        year = year,
                        author_list = row["author"],
                        url = row["source_url"],
                    )
                    people = People.objects_unfiltered.get(user__id=row["uploaded_by_id"])
                    RecordRelationship.objects.create(
                        relationship_id = 11,
                        record_parent = people,
                        record_child = info,
                    )
                    author = row["author"],
                    check = People.objects.filter(name=author)
                    if check:
                        people = check[0]
                        RecordRelationship.objects.create(
                            relationship_id = 4,
                            record_parent = people,
                            record_child = info,
                        )
                    space_id = row["secondary_space_id"] if row["secondary_space_id"] else row["primary_space_id"]
                    info.spaces.add(ReferenceSpace.objects.get(old_id=space_id))
        elif request.GET["table"] == "referencespaces":
            if int(request.GET["start"]) == 0:
                ReferenceSpaceLocation.objects.all().delete()
                ReferenceSpace.objects_unfiltered.all().delete()

            if "creategeo" in request.GET:
                GeocodeScheme.objects.all().delete()
                list = [
                    {
                        "name": "System Types",
                        "icon": "fal fa-fw fa-layer-group",
                        "items": ["Company", "Island", "Rural", "Urban", "Household"],
                    },
                    {
                        "name": "UN Statistics Division Groupings",
                        "icon": "fal fa-fw fa-universal-access",
                        "items": ["Least Developed Countries", "Land Locked Developing Countries", "Small Island Developing States", "Developed Regions", "Developing Regions"],
                    },
                    {
                        "name": "NUTS",
                        "icon": "fal fa-fw fa-globe-europe",
                        "items": ["NUTS 1"],
                        "items2": ["NUTS 2"],
                        "items3": ["NUTS 3"],
                        "items4": ["Local Administrative Unit (LAU)"],
                    },
                    {
                        "name": "ISO 3166-1",
                        "icon": "fal fa-fw fa-globe",
                        "items": ["Countries"],
                    },
                    {
                        "name": "Sector: Hotels and lodging",
                        "icon": "fal fa-fw fa-bed",
                        "items": ["Hotels", "Camping grounds"],
                    },
                    {
                        "name": "Sector: Transport",
                        "icon": "fal fa-fw fa-car",
                        "items": ["Bus stops", "Train stations", "Bicycle racks", "Bridges", "Electric charging stations", "Lighthouses", "Airports", "Ports", "Border Crossings"],
                    },
                    {
                        "name": "Sector: Water and sanitation",
                        "icon": "fal fa-fw fa-water",
                        "items": ["Marine outfalls", "Dams", "Water reservoirs", "Wastewater treatment plants", "Water treatment plants", "Pumping stations"],
                    },
                    {
                        "name": "Sector: Agriculture",
                        "icon": "fal fa-fw fa-seedling",
                        "items": ["Farms"],
                    },
                    {
                        "name": "Sector: Mining",
                        "icon": "fal fa-fw fa-digging",
                        "items": ["Mines"],
                    },
                    {
                        "name": "Sector: Construction",
                        "icon": "fal fa-fw fa-construction",
                        "items": ["Building site"],
                    },
                    {
                        "name": "Sector: Energy",
                        "icon": "fal fa-fw fa-bolt",
                        "items": ["Wind turbines", "Solar parks/farms", "Roof-top solar panels", "Power plants", "High voltage lines", "Substations", "Transmission masts"],
                    },
                    {
                        "name": "Sector: Waste",
                        "icon": "fal fa-fw fa-dumpster",
                        "items": ["Waste transfer station", "Waste drop-off sites", "Waste incinerators", "Landfills"],
                    },
                    {
                        "name": "Sector: Storage",
                        "icon": "fal fa-fw fa-container",
                        "items": ["Fuel storage facilities", "Energy storage"],
                    },
                    {
                        "name": "Sector: Fishing",
                        "icon": "fal fa-fw fa-fish",
                        "items": ["Fish farms"],
                    },
                    {
                        "name": "Sector: Food service",
                        "icon": "fal fa-fw fa-utensils",
                        "items": ["Restaurants", "Bars"],
                    },
                    {
                        "name": "Sector: Forestry",
                        "icon": "fal fa-fw fa-trees",
                        "items": ["Plantation"],
                    },
                    {
                        "name": "Sector: Manufacturing (Food)",
                        "icon": "fal fa-fw fa-hamburger",
                        "items": ["Abbatoir", "Bakery", "Bread mill", "Food processing facilities"],
                    },
                    {
                        "name": "Sector: Manufacturing (coke and petroleum products)",
                        "icon": "fal fa-fw fa-oil-can",
                        "items": ["Refineries"],
                    },
                    {
                        "name": "Subdivisions of South Africa",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Provinces"],
                        "items2": ["Metropolitan municipalities", "District municipalities"],
                        "items3": ["Local municipalilties"],
                        "items4": ["Wards"],
                    },
                    {
                        "name": "Subdivisions of Nicaragua",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Departments", "Autonomous regions"],
                        "items2": ["Municipalities"],
                    },
                    {
                        "name": "Subdivisions of Costa Rica",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Provinces"],
                        "items2": ["Cantons"],
                        "items3": ["Districts"],
                    },
                    {
                        "name": "Areas of France",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Ilots Regroupés pour l'information statistique (IRIS)", "Commune"],
                    },
                    {
                        "name": "Areas of Singapore",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Master Plan 2014 Subzones"],
                    },
                    {
                        "name": "Areas of Canada",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Neighbourhoods"],
                    },
                    {
                        "name": "Areas of South Africa",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Suburbs"],
                    },
                    {
                        "name": "Areas of the world",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Supra-national territory", "Sub-national territory"],
                    },
                    {
                        "name": "Areas of The Netherlands",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Buurten", "Stadsdelen", "Wijken"],
                    },
                    {
                        "name": "Areas of Belgium",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Quartiers", "Communes"],
                    },
                    {
                        "name": "Subdivisions of Grenada",
                        "icon": "fal fa-fw fa-flag",
                        "items": ["Parishes", "Dependencies"],
                    },

                ]
                for each in list:
                    scheme = GeocodeScheme.objects.create(
                        name = each["name"],
                        is_comprehensive = False,
                        icon = each["icon"],
                    )
                    for name in each["items"]:
                        Geocode.objects.create(
                            scheme = scheme,
                            name = name,
                            depth = 1,
                        )
                    if "items2" in each:
                        for name in each["items2"]:
                            Geocode.objects.create(
                                scheme = scheme,
                                name = name,
                                depth = 2,
                            )
                    if "items3" in each:
                        for name in each["items3"]:
                            Geocode.objects.create(
                                scheme = scheme,
                                name = name,
                                depth = 3,
                            )
                    if "items4" in each:
                        for name in each["items4"]:
                            Geocode.objects.create(
                                scheme = scheme,
                                name = name,
                                depth = 4,
                            )


            checkward = Geocode.objects.filter(name="Wards")
            checkcities = Geocode.objects.filter(name="Urban")
            checkcountries = Geocode.objects.filter(name="Countries")
            checkisland = Geocode.objects.filter(name="Island")
            count = 0
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    count = count+1
                    print(count)
                    if count >= int(request.GET["start"]) and count < int(request.GET["end"]):
                        deleted = False if row["active"] == "t" else True
                        space = ReferenceSpace.objects.create(
                            old_id = row["id"],
                            name = row["name"],
                            description = row["description"],
                            slug = row["slug"],
                            is_deleted = deleted,
                        )
                        if int(row["type_id"]) == 45 and checkward:
                            space.geocodes.add(checkward[0])
                        elif int(row["type_id"]) == 3 and checkcities:
                            space.geocodes.add(checkcities[0])
                        elif int(row["type_id"]) == 2 and checkcountries:
                            space.geocodes.add(checkcountries[0])
                        elif int(row["type_id"]) == 21 and checkisland:
                            space.geocodes.add(checkisland[0])
                        elif int(row["type_id"]) == 56:
                            space.geocodes.add(Geocode.objects.get(name="Ilots Regroupés pour l'information statistique (IRIS)"))
                        elif int(row["type_id"]) == 50:
                            space.geocodes.add(Geocode.objects.get(name="Master Plan 2014 Subzones"))
                        elif int(row["type_id"]) == 49:
                            space.geocodes.add(Geocode.objects.get(name="Border Crossings"))
                        elif int(row["type_id"]) == 47:
                            space.geocodes.add(Geocode.objects.get(name="Neighbourhoods"))
                        elif int(row["type_id"]) == 46:
                            space.geocodes.add(Geocode.objects.get(name="Suburbs"))
                        elif int(row["type_id"]) == 44:
                            space.geocodes.add(Geocode.objects.get(name="Supra-national territory"))
                        elif int(row["type_id"]) == 43:
                            space.geocodes.add(Geocode.objects.get(name="Sub-national territory"))
                        elif int(row["type_id"]) == 42:
                            space.geocodes.add(Geocode.objects.get(name="Bus stops"))
                        elif int(row["type_id"]) == 41:
                            space.geocodes.add(Geocode.objects.get(name="Train stations"))
                        elif int(row["type_id"]) == 40:
                            space.geocodes.add(Geocode.objects.get(name="Transmission masts"))
                        elif int(row["type_id"]) == 39:
                            space.geocodes.add(Geocode.objects.get(name="Pumping stations"))
                        elif int(row["type_id"]) == 38:
                            space.geocodes.add(Geocode.objects.get(name="Bicycle racks"))
                        elif int(row["type_id"]) == 37:
                            space.geocodes.add(Geocode.objects.get(name="Bridges"))
                        elif int(row["type_id"]) == 36:
                            space.geocodes.add(Geocode.objects.get(name="Wind turbines"))
                        elif int(row["type_id"]) == 35:
                            space.geocodes.add(Geocode.objects.get(name="Electric charging stations"))
                        elif int(row["type_id"]) == 34:
                            space.geocodes.add(Geocode.objects.get(name="Buurten"))
                        elif int(row["type_id"]) == 32:
                            space.geocodes.add(Geocode.objects.get(name="Parishes"))
                        elif int(row["type_id"]) == 31:
                            space.geocodes.add(Geocode.objects.get(name="Quartiers"))
                        elif int(row["type_id"]) == 30:
                            space.geocodes.add(Geocode.objects.get(name="Communes"))
                        elif int(row["type_id"]) == 29:
                            space.geocodes.add(Geocode.objects.get(name="Stadsdelen"))
                        elif int(row["type_id"]) == 28:
                            space.geocodes.add(Geocode.objects.get(name="Wijken"))
                        elif int(row["type_id"]) == 27:
                            space.geocodes.add(Geocode.objects.get(name="Marine outfalls"))
                        elif int(row["type_id"]) == 26:
                            space.geocodes.add(Geocode.objects.get(name="Lighthouses"))
                        elif int(row["type_id"]) == 25:
                            space.geocodes.add(Geocode.objects.get(name="Airports"))
                        elif int(row["type_id"]) == 24:
                            space.geocodes.add(Geocode.objects.get(name="Fuel storage facilities"))
                        elif int(row["type_id"]) == 23:
                            space.geocodes.add(Geocode.objects.get(name="Waste transfer station"))
                        elif int(row["type_id"]) == 22:
                            space.geocodes.add(Geocode.objects.get(name="Waste drop-off sites"))
                        elif int(row["type_id"]) == 19:
                            space.geocodes.add(Geocode.objects.get(name="Energy storage"))
                        elif int(row["type_id"]) == 18:
                            space.geocodes.add(Geocode.objects.get(name="Waste incinerators"))
                        elif int(row["type_id"]) == 17:
                            space.geocodes.add(Geocode.objects.get(name="Landfills"))
                        elif int(row["type_id"]) == 16:
                            space.geocodes.add(Geocode.objects.get(name="Food processing facilities"))
                        elif int(row["type_id"]) == 15:
                            space.geocodes.add(Geocode.objects.get(name="Farms"))
                        elif int(row["type_id"]) == 14:
                            space.geocodes.add(Geocode.objects.get(name="Mines"))
                        elif int(row["type_id"]) == 13:
                            space.geocodes.add(Geocode.objects.get(name="Ports"))
                        elif int(row["type_id"]) == 12:
                            space.geocodes.add(Geocode.objects.get(name="Power plants"))
                        elif int(row["type_id"]) == 11:
                            space.geocodes.add(Geocode.objects.get(name="Refineries"))
                        elif int(row["type_id"]) == 9:
                            space.geocodes.add(Geocode.objects.get(name="Dams"))
                        elif int(row["type_id"]) == 8:
                            space.geocodes.add(Geocode.objects.get(name="Water reservoirs"))
                        elif int(row["type_id"]) == 7:
                            space.geocodes.add(Geocode.objects.get(name="Wastewater treatment plants"))
                        elif int(row["type_id"]) == 6:
                            space.geocodes.add(Geocode.objects.get(name="Water treatment plants"))

        elif request.GET["table"] == "dataviz":
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    info = LibraryItem.objects.get(old_id=row["id"], name=row["title"])
                    print(info)
                    if row["space_id"]:
                        info.spaces.add(ReferenceSpace.objects.get(old_id=row["space_id"]))
                        print("Adding space!")
                    if row["process_group_id"]:
                        info.sectors.add(Sector.objects.get(old_id=row["process_group_id"]))
                        print("Adding sector!")

        elif request.GET["table"] == "referencespacelocations":
            import sys
            csv.field_size_limit(sys.maxsize)
            from django.contrib.gis.geos import Point
            from django.contrib.gis.geos import GEOSGeometry

            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    check = ReferenceSpaceLocation.objects.filter(pk=row["id"])
                    if not check:
                        try:
                            lat = float(row["lat"])
                            lng = float(row["lng"])
                        except:
                            lat = None
                            lng = None
                        if row["geojson"] or lat:
                            deleted = True if not row["active"] else False
                            start = row["start"] if row["start"] else None
                            end = row["end"] if row["end"] else None
                            if row["geojson"]:
                                try:
                                    geometry = GEOSGeometry(row["geojson"])
                                except Exception as e:
                                    print("Houston, we have a problem!")
                                    print(e)
                                    print(row["id"])
                            elif lat and lng:
                                geometry = Point(lng, lat)
                            try:
                                location = ReferenceSpaceLocation.objects.create(
                                    id = row["id"],
                                    space = ReferenceSpace.objects.get(old_id=row["space_id"]),
                                    description = row["description"],
                                    start = start,
                                    end = end,
                                    is_deleted = deleted,
                                    geometry = geometry,
                                )
                                space = ReferenceSpace.objects.get(old_id=row["space_id"])
                                space.location = location
                                space.save()
                            except Exception as e:
                                print("Not imported because there is an error")
                                print(e)
                                print(row["space_id"])
        elif request.GET["table"] == "flowdiagrams":
            FlowDiagram.objects.all().delete()
            water = FlowDiagram.objects.create(name="Urban water cycle")
            def activity(id):
                a = Activity.objects.get(old_id=id)
                return a.id
            FlowBlocks.objects.create(origin_id=activity(67), origin_label="Rain, rivers, and other natural water processes", destination_id=activity(398932), destination_label="Collection of water in dams", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(398932), origin_label="Collection of water in dams", destination_id=activity(67), destination_label="Evaporation, leaking, and losses of water", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(398932), origin_label="Collection of water in dams", destination_id=activity(398932), destination_label="Water treatment", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(398932), origin_label="Water treatment", destination_id=activity(399133), destination_label="Reservoirs", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(398932), origin_label="Water treatment", destination_id=activity(67), destination_label="Evaporation, leaking, and losses of water", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(399133), origin_label="Reservoirs", destination_id=activity(67), destination_label="Evaporation, leaking, and losses of water", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(399133), origin_label="Reservoirs", destination_id=activity(399468), destination_label="Water consumption", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(399468), origin_label="Water consumption", destination_id=activity(67), destination_label="Evaporation, leaking, and losses of water", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(399468), origin_label="Water consumption", destination_id=activity(398935), destination_label="Wastewater treatment", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(398935), origin_label="Wastewater treatment", destination_id=activity(67), destination_label="Evaporation, leaking, and losses of water", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(398935), origin_label="Wastewater treatment", destination_id=activity(67), destination_label="Rain, rivers, and other natural water processes", diagram=water)
            FlowBlocks.objects.create(origin_id=activity(398935), origin_label="Wastewater treatment", destination_id=activity(399468), destination_label="Water consumption", diagram=water)


        # Temp import stuff
        if "import" in request.GET:
            import csv
            # Let's import the individual materials...
            file = settings.MEDIA_ROOT + "/import/materials.csv"
            latest = Material.objects.all().order_by("-old_id")[0]
            latest = latest.old_id
            print(latest)

            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                catalogs = {}
                for row in contents:
                    id = row["id"]
                    if int(id) > int(latest):
                        catalog = row["catalog_id"]
                        name = row["name"]
                        if len(name) > 255:
                            name = name[0:255]
                            description = "Full name: " + row["name"]
                        else:
                            description = row["description"]
                        if catalog not in catalogs:
                            check = MaterialCatalog.objects.get(old_id=row["catalog_id"])
                            catalogs[catalog] = check
                        Material.objects.create(
                            old_id = id,
                            name = name,
                            code = row["code"],
                            catalog = catalogs[catalog],
                            description = description,
                        )

        # Quick copy import script
        if "import" in request.GET:
            import csv
            matches = {
                "1": 753,
                "2": 752,
                "3": 751,
                "4": 750,
                "5": 754,
                "6": 799,
            }

            file = settings.MEDIA_ROOT + "/import/videocollections.csv"
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    video = row["video_id"]
                    collection = row["videocollection_id"]
                    try:
                        match = matches[collection]
                        video = Video.objects.get(old_id=video)
                        print(match)
                        print(video)
                        video.tags.add(Tag.objects.get(pk=match))
                    except Exception as e:
                        print("PROBLEMO!!")
                        print(e)

        if error:
            messages.error(request, "We could not import your data")
        else:
            messages.success(request, "Data was imported")
    context = {
        "tags": Tag.objects.all().count(),
        "activities": Activity.objects.all().count(),
        "projects": Project.objects.all().count(),
        "organizations": Organization.objects.all().count(),
        "videos": Video.objects.all().count(),
        "people": People.objects.all().count(),
        "spaces": ReferenceSpace.objects.all().count(),
        "locations": ReferenceSpaceLocation.objects.all().count(),
        "libraryitems": LibraryItem.objects.all().count(),
        "librarytypes": LibraryItemType.objects.all().count(),
        "tttt": Tag.objects.all().count(),
        "publishers": Organization.objects.filter(type="publisher").count(),
        "news": News.objects.all().count(),
        "blogs": Blog.objects.all().count(),
        "events": Event.objects.all().count(),
        "journals": Organization.objects.filter(type="journal").count(),
        "publications": LibraryItem.objects.all().count(),
        "users": User.objects.all().count(),
        "photos": Photo.objects.all().count(),
        "sectors": Sector.objects.all().count(),
        "sectoractivities": Sector.activities.through.objects.all().count(),
        "librarytags": LibraryItem.tags.through.objects.all().count(),
        "libraryspaces": LibraryItem.spaces.through.objects.all().count(),
        "spacesectors": ReferenceSpace.sectors.through.objects.all().count(),
        "flowdiagrams": FlowDiagram.objects.all().count(),
        "dataviz": LibraryItem.objects.filter(type__name="Image").count(),
        "flowblocks": FlowBlocks.objects.all().count(),
        "podcasts": LibraryItem.objects.filter(type__name="Podcast").count(),
        "project_team_members": RecordRelationship.objects.filter(relationship__name__in=["Team member", "Former team member"]).count(),
    }
    return render(request, "temp.import.html", context)


# These are permanent redirects to sort out old URL patterns 
# At some point, say Dec 2021, we should just remove this

def redirect_publication(request, id):
    info = get_object_or_404(LibraryItem, old_id=id)
    return redirect(info.get_full_url(), permanent=True)

