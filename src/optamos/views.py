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

def calculate_consistency_ratio(project):
    """
    Calculate the Consistency Ratio (CR) for all Criteria of this project
    We calculate this using numpy -- all we need is the CR itself to show on 
    each page. On the results page we calculate it differently but it's left
    separate intentionally to use it as a check that both procedures yield the 
    same results.
    
    Returns:
        float: CR value
    """
    # Step 1: Load all criteria and scores
    criteria = list(project.criteria.all())
    n = len(criteria)
    if n < 2:
        return 0.0  # trivial case

    # Step 2: Build matrix
    matrix = np.ones((n, n))  # diagonal = 1 automatically
    crit_id_to_index = {c.id: idx for idx, c in enumerate(criteria)}

    for score in OptamosCriteriaValue.objects.filter(criteria1__project=project):
        i = crit_id_to_index[score.criteria1.id]
        j = crit_id_to_index[score.criteria2.id]
        matrix[i, j] = score.value1
        matrix[j, i] = score.value2

    # Step 3: Compute principal eigenvalue
    eigenvalues, _ = np.linalg.eig(matrix)
    lambda_max = max(eigenvalues.real)

    # Step 4: Consistency Index (CI)
    ci = (lambda_max - n) / (n - 1)

    # Step 5: Random Index (RI)
    ri_dict = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45, 10:1.49}
    ri = ri_dict.get(n, 0)
    if ri == 0:
        return 0.0

    # Step 6: CR
    cr = ci / ri
    return cr

def create_matrix(project):
    # Create a matrix with all criteria (values are 0 for each item)
    matrix_criteria = list(project.criteria.all())

    criteria_ids = [c.id for c in matrix_criteria]
    matrix = {
        c1.id: {c2.id: (1 if c1.id == c2.id else 0) for c2 in matrix_criteria} # Default if 0 if not set, but 1 for the diagonal values
        for c1 in matrix_criteria
    }

    # Load the actual scores into the matrix
    for score in OptamosCriteriaValue.objects.filter(criteria1__project=project):
        c1 = score.criteria1.id
        c2 = score.criteria2.id
        matrix[c1][c2] = score.value1
        matrix[c2][c1] = score.value2

    return matrix

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
            next_criteria = project.criteria.filter(pk__gt=criteria.pk).order_by("name").first()
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
        "criteria_list": project.criteria.all().order_by("id").annotate(is_done=Count("option_pairs")),
        "criteria_values": OptamosCriteriaValue.objects.filter(criteria1__project=project).count(), 
        # Count how many there theoretically are, so that we can verify that all are saved -- this is particularly 
        # relevant in case people edit the project and add criteria in which case we need to show an error
        "total_required_criteria_values": len(list(combinations(project.criteria.all(), 2))), 
        "menu": "projects",
        "cr": calculate_consistency_ratio(project),
    }

    return render(request, "optamos/project.html", context)

def project_results(request, id):

    if not request.user.is_authenticated:
        return redirect("optamos:login")

    project = OptamosProject.objects_include_private.filter(pk=id, user=request.user).first()
    if not project:
        messages.error(request, "Project is not found - either it does not exist or you do not have access. Below are your projects.")
        return redirect("optamos:projects")


    # START OF CRITERIA EVALUATION
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

    matrix = create_matrix(project)
    matrix_criteria = list(project.criteria.all())

    # Give the proper labels to the matrix columns and rows
    named_matrix = {
        c1.name: {
            c2.name: matrix[c1.id][c2.id]
            for c2 in matrix_criteria
        }
        for c1 in matrix_criteria
    }

    # Initialize totals per column
    column_totals = {c.id: 0 for c in matrix_criteria}

    # Sum column values
    for row in matrix_criteria:
        for col in matrix_criteria:
            column_totals[col.id] += matrix[row.id][col.id]

    # Normalized matrix
    normalized_matrix_criteria = {
        row.id: {} for row in matrix_criteria
    }

    for row in matrix_criteria:
        for col in matrix_criteria:
            total = column_totals[col.id]

            if total != 0:
                normalized_matrix_criteria[row.id][col.id] = (
                    matrix[row.id][col.id] / total
                )
            else:
                normalized_matrix_criteria[row.id][col.id] = 0

    # Calculate the total and the average for each row in the normalized matrix
    row_totals = {}
    row_averages = {}

    num_criteria = len(matrix_criteria)

    for row in matrix_criteria:
        total = 0
        for col in matrix_criteria:
            total += normalized_matrix_criteria[row.id][col.id]

        row_totals[row.id] = total
        row_averages[row.id] = (
            total / num_criteria if num_criteria > 0 else 0
        )

    # END OF CRITERIA EVALUTION

    # CONSISTENCY RATIO CALCULATION
    # Step 1: Compute weighted sum vector

    weighted_sum = {}

    for row in matrix_criteria:
        total = 0
        for col in matrix_criteria:
            total += matrix[row.id][col.id] * row_averages[col.id]
        weighted_sum[row.id] = total

    # Step 2: Compute consistency vector (λ values)
    lambda_values = {}

    for row in matrix_criteria:
        weight = row_averages[row.id]
        lambda_values[row.id] = (
            weighted_sum[row.id] / weight if weight != 0 else 0
        )

    # Step 3: Compute λₘₐₓ (principal eigenvalue)
    n = len(matrix_criteria)
    lambda_max = sum(lambda_values.values()) / n if n > 0 else 0

    # Step 4: Compute Consistency Index (CI)
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0

    # Step 5: Compute Consistency Ratio (CR)

    # Random Index (RI) table (Saaty)
    RI_TABLE = {
        1: 0.00,
        2: 0.00,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49,
    }

    ri = RI_TABLE.get(n, 1.49)  # fallback for n > 10
    cr = ci / ri if ri != 0 else 0

    # START OF OPTIONS EVALATION

    # Get all criteria and options
    criteria = list(OptamosCriteria.objects.filter(project=project))
    options = list(OptamosOption.objects.filter(project=project))
    option_values = OptamosOptionValue.objects.filter(criteria__project=project)

    # Step 1: Initialize matrices per criterion
    option_matrices = {}
    for c in criteria:
        option_matrices[c.id] = {
            o1.id: {o2.id: 1 if o1.id == o2.id else 0 for o2 in options}
            for o1 in options
        }

    # Step 2: Fill matrices with OptionValue data
    for ov in option_values:
        c_id = ov.criteria.id
        o1_id = ov.option1.id
        o2_id = ov.option2.id
        value = ov.value

        # Fill reciprocal matrix
        if value > 0:
            value += 1
            option_matrices[c_id][o2_id][o1_id] = value
            option_matrices[c_id][o1_id][o2_id] = 1/value
        elif value < 0:
            value -= 1
            option_matrices[c_id][o2_id][o1_id] = 1/-value
            option_matrices[c_id][o1_id][o2_id] = -value
        else:
            option_matrices[c_id][o1_id][o2_id] = 1
            option_matrices[c_id][o2_id][o1_id] = 1

    # Step 3: Normalize matrices and compute option weights
    normalized_option_matrices = {}
    option_weights = {}  # row averages per criterion

    for c in criteria:
        matrix = option_matrices[c.id]

        # Compute column totals
        col_totals = {o.id: 0 for o in options}
        for col in options:
            for row in options:
                col_totals[col.id] += matrix[row.id][col.id]

        # Normalize matrix
        normalized_matrix = {}
        for row in options:
            normalized_matrix[row.id] = {}
            for col in options:
                total = col_totals[col.id]
                normalized_matrix[row.id][col.id] = (
                    matrix[row.id][col.id] / total if total != 0 else 0
                )

        normalized_option_matrices[c.id] = normalized_matrix

        # Compute row averages → option weights for this criterion
        row_avg = {}
        for row in options:
            total = sum(normalized_matrix[row.id][col.id] for col in options)
            row_avg[row.id] = total / len(options)
        option_weights[c.id] = row_avg

    # END OF OPTIONS EVALUATION


    # Calculate global scores

    global_scores = {o.id: 0 for o in options}

    for o in options:
        total_score = 0
        for c in criteria:
            weight_c = row_averages[c.id]  # criteria weight
            weight_o = option_weights[c.id][o.id]  # option weight under this criterion
            total_score += weight_c * weight_o
        global_scores[o.id] = total_score

    global_ranking = sorted(
        [{'option': o, 'score': global_scores[o.id]} for o in options],
        key=lambda x: x['score'],
        reverse=True  # highest score first
    )

    # Compute CR per criterion
    ri_dict = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45, 10:1.49}
    option_crs = {}

    n_options = len(options)
    option_id_to_index = {o.id: idx for idx, o in enumerate(options)}

    for c in criteria:
        # build matrix
        c_matrix = np.ones((n_options, n_options))
        for ov in option_values.filter(criteria=c):
            i = option_id_to_index[ov.option1.id]
            j = option_id_to_index[ov.option2.id]

            # Fill reciprocal matrix
            c_matrix[i, j] = ov.value1
            c_matrix[j, i] = ov.value2

        # compute CR
        if n_options < 2:
            c_cr = 0.0
        else:
            eigenvalues, _ = np.linalg.eig(c_matrix)
            c_lambda_max = max(eigenvalues.real)
            c_ci = (c_lambda_max - n_options) / (n_options - 1)
            c_ri = ri_dict.get(n_options, 0)
            c_cr = c_ci / c_ri if c_ri != 0 else 0.0

        option_crs[c.id] = c_cr

    # Build a summary taable

    summary_table = []

    for c in criteria:
        row = {
            "criterion": c.name,
            "options": [
                option_weights[c.id][o.id] * row_averages[c.id] * 100
                for o in options
            ],
            "cr": option_crs[c.id],
            "importance": row_averages[c.id] * 100
        }
        summary_table.append(row)

    # Compute totals for each option column
    totals = []
    n_options = len(options)
    for idx in range(n_options):
        total = sum(row["options"][idx] for row in summary_table)
        totals.append(total)

    context = {
        "bg": random.choice(OPTAMOS_BG),
        "project": project,
        "remove_padding_main_container": True,
        "criteria": criteria,
        "page": "results",
        "criteria_list": project.criteria.all().order_by("id").annotate(is_done=Count("option_pairs")),
        "criteria_values": OptamosCriteriaValue.objects.filter(criteria1__project=project).count(), 
        # Count how many there theoretically are, so that we can verify that all are saved -- this is particularly 
        # relevant in case people edit the project and add criteria in which case we need to show an error
        "total_required_criteria_values": len(list(combinations(project.criteria.all(), 2))), 
        "menu": "projects",

        "criteria": criteria,
        "options": options,
        "option_matrices": option_matrices,
        "normalized_option_matrices": normalized_option_matrices,
        "option_weights": option_weights,

        "global_scores": global_scores,
        "global_ranking": global_ranking,
        "option_crs": option_crs,
        "summary_table": summary_table,
        "summary_totals": totals,

        "points_criteria": points_criteria,
        "points_options": points_options,
        "matrix": named_matrix,
        "matrix_criteria": matrix_criteria,
        "column_totals": column_totals,
        "normalized_matrix": normalized_matrix_criteria,
        "row_totals": row_totals,
        "row_averages": row_averages,
        "lambda_max": lambda_max,
        "ci": ci,
        "cr": cr,
    }

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
