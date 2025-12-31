from core.models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from itertools import combinations
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
        "menu": "index",
    }
    return render(request, "optamos/index.html", context)

def projects(request):
    if not request.user.is_authenticated:
        return redirect("optamos:login")

    projects = OptamosProject.objects_include_private.filter(user=request.user)

    if "delete" in request.GET:
        project = projects.get(uid=request.GET["delete"])
        project.delete()
        messages.success(request, f"Project {project.name} has been deleted.")
        return redirect(request.path)

    context = {
        "bg": random.choice(OPTAMOS_BG),
        "projects": projects,
        "menu": "projects",
    }
    return render(request, "optamos/projects.html", context)

def project_create(request):

    if not request.user.is_authenticated:
        return redirect("optamos:login")

    if request.method == "POST":
        project = OptamosProject()
        project.is_public = False
        project.name = request.POST.get("name")
        project.goal = request.POST.get("goal")
        project.save()

        project.user.add(request.user)

        if request.POST.getlist("option"):
            for each in request.POST.getlist("option"):
                if each:
                    OptamosOption.objects.create(project=project, name=each)

        if (criteria_list := request.POST.get("criteria")):
            for criteria in criteria_list.split("\n"):
                if criteria:
                    OptamosCriteria.objects.create(project=project, name=criteria.strip())

        return redirect(reverse("optamos:project", args=[project.uid]))

    context = {
        "bg": random.choice(OPTAMOS_BG),
        "menu": "projects",
    }
    return render(request, "optamos/project.create.html", context)

def project_settings(request, id):

    if not request.user.is_authenticated:
        return redirect("optamos:login")

    project = OptamosProject.objects_include_private.filter(pk=id, user=request.user).first()
    if not project:
        return redirect("optamos:login")

    if request.method == "POST":
        project.name = request.POST.get("name")
        project.goal = request.POST.get("goal")
        project.save()

        for each in project.options.all():
            label = f"option_{each.id}"
            if request.POST.get(label):
                each.name = request.POST[label]
                each.save()
            else:
                each.delete()

        for each in project.criteria.all():
            label = f"criteria_{each.id}"
            if request.POST.get(label):
                each.name = request.POST[label]
                each.save()
            else:
                each.delete()

        if request.POST.getlist("option"):
            for each in request.POST.getlist("option"):
                if each:
                    OptamosOption.objects.create(project=project, name=each)

        if request.POST.getlist("criteria"):
            for each in request.POST.getlist("criteria"):
                if each:
                    OptamosCriteria.objects.create(project=project, name=each)

        messages.success(request, "Changes have been saved.")
        return redirect(reverse("optamos:project", args=[project.uid]))

    context = {
        "bg": random.choice(OPTAMOS_BG),
        "projects": project,
        "menu": "projects",
        "project": project,
    }
    return render(request, "optamos/project.settings.html", context)

def project(request, id, page="home"):

    if not request.user.is_authenticated:
        return redirect("optamos:login")

    project = OptamosProject.objects_include_private.filter(pk=id, user=request.user).first()
    if not project:
        messages.error(request, "Project is not found - either it does not exist or you do not have access. Below are your projects.")
        return redirect("optamos:projects")

    values = {}
    pairs = None

    if (criteria := request.GET.get("criteria")):
        page = "criteria"
        criteria = OptamosCriteria.objects.get(project=project, pk=criteria)

        # Let's create a dict with the names of the <input> fields and the value for them
        # so we can load them into the form
        for each in OptamosOptionValue.objects.filter(criteria=criteria):
            value = f"range-{each.option1_id}-{each.option2_id}"
            values[value] = each.value

        # This creates pairs of all possible combinations of options
        pairs = list(combinations(project.options.all(), 2))

    elif "rank_all_criteria" in request.GET:
        page = "rank_all_criteria"
        # Let's create a dict with the names of the <input> fields and the value for them
        # so we can load them into the form
        for each in OptamosCriteriaValue.objects.filter(criteria1__project=project):
            value = f"range-{each.criteria1_id}-{each.criteria2_id}"
            values[value] = each.value

        # This creates pairs of all possible combinations of options
        pairs = list(combinations(project.criteria.all(), 2))

    elif page == "results":
        points_options = {}
        points_criteria = {}
        for each in project.options.all():
            points_options[each] = 0
        for each in project.criteria.all():
            points_criteria[each] = 0
        for each in OptamosCriteriaValue.objects.filter(criteria1__project=project):
            if each.value > 0:
                points_criteria[each.criteria2] += each.value
            elif each.value < 0:
                points_criteria[each.criteria1] += each.value*-1
        for each in OptamosOptionValue.objects.filter(criteria__project=project):
            if each.value > 0:
                points_options[each.option2] += each.value
            elif each.value < 0:
                points_options[each.option1] += each.value*-1

    if request.method == "POST":
        if page == "criteria":
            OptamosOptionValue.objects.filter(criteria=criteria).delete()
            for option1,option2 in pairs:
                # This creates the name of the relevant input field
                value = f"range-{option1.id}-{option2.id}"
                OptamosOptionValue.objects.create(
                    option1 = option1,
                    option2 = option2,
                    criteria = criteria,
                    value = request.POST[value],
                )
            next_criteria = project.criteria.filter(pk__gt=criteria.pk).first()
            if next_criteria:
                return redirect(reverse("optamos:project", args=[project.uid]) + f"?criteria={next_criteria.id}")
            else:
                return redirect(reverse("optamos:project", args=[project.uid]) + "?rank_all_criteria=true")

        elif page == "rank_all_criteria":
            OptamosCriteriaValue.objects.filter(criteria1__project=project).delete()
            for criteria1,criteria2 in pairs:
                # This creates the name of the relevant input field
                value = f"range-{criteria1.id}-{criteria2.id}"
                OptamosCriteriaValue.objects.create(
                    criteria1 = criteria1,
                    criteria2 = criteria2,
                    value = request.POST[value],
                )
            return redirect(reverse("optamos:project_results", args=[project.uid]))

    context = {
        "bg": random.choice(OPTAMOS_BG),
        "project": project,
        "remove_padding_main_container": True,
        "criteria": criteria,
        "pairs": pairs,
        "values": values,
        "page": page,
        "criteria_list": project.criteria.all().annotate(is_done=Count("option_pairs")),
        "criteria_values": OptamosCriteriaValue.objects.filter(criteria1__project=project).count(), 
        # Count how many there theoretically are, so that we can verify that all are saved -- this is particularly 
        # relevant in case people edit the project and add criteria in which case we need to show an error
        "total_required_criteria_values": len(list(combinations(project.criteria.all(), 2))), 
        "menu": "projects",
    }

    if page == "results":
        context["points_criteria"] = points_criteria
        context["points_options"] = points_options

    return render(request, "optamos/project.html", context)

# ACCOUNT-RELATED FUNCTIONS

def account_login(request):
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        redirect_url = request.GET.get("redirect", "optamos:projects")

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
        "menu": "login",
    }
    return render(request, "optamos/login.html", context)

def account_logout(request):
    logout(request)
    messages.success(request, "You are now logged out")
    return redirect("optamos:index")

def account(request):
    if not request.user.is_authenticated:
        return redirect("optamos:login")

    context = {
        "bg": random.choice(OPTAMOS_BG),
        "projects": OptamosProject.objects_include_private.filter(user=request.user),
        "menu": "account",
    }
    return render(request, "optamos/account.settings.html", context)

def account_create(request):

    redirect_url = request.GET.get("next") if request.GET.get("next") else reverse("optamos:projects")

    if request.user.is_authenticated:
        is_logged_in = True
        return redirect(redirect_url)

    if request.method == "POST":
        error = None
        password = request.POST.get("password")
        email = request.POST.get("email")
        name = request.POST.get("name")
        if request.POST.get("phone").lower() != "good morning":
            messages.error(request, "Please enter 'Good morning' in the last box.")
            error = True
        elif not password:
            messages.error(request, "You did not enter a password.")
            error = True
        elif User.objects.filter(email=email).exists():
            url = reverse("optamos:login")
            messages.error(request, f"An account already exists with this e-mail address. Please <a href='{url}'>log in</a>. <br>Remember that Metabolism of Islands accounts also work to log into OPTamos.")
            error = True

        if not error:
            user = User.objects.create_user(email, email, password)
            user.first_name = name
            user.is_superuser = False
            user.is_staff = False
            user.save()
            login(request, user)

            people = People.objects.create(name=name, email=user.email)
            people.user = user
            people.meta_data = {}
            people.save()

            messages.success(request, "You are successfully registered.")

            return redirect(redirect_url)

    context = {
        "bg": random.choice(OPTAMOS_BG),
    }
    return render(request, "optamos/account.html", context)
