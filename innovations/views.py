from django.contrib.auth.decorators import login_required
from django.db.models import Model
from django.http import Http404

from django.shortcuts import render, redirect

from innovations.models import Innovation
from signup.groups import administrators, committee_members, in_groups


@login_required
def my_innovations(request):
    innovations = get_filtered_innovations(issuer=request.user)
    return render(request, "innovations/innovations_list.html", {"innovations": innovations})


@login_required
def with_status(request, status):
    if is_forbidden(status, request.user):
        raise Http404("Page not found!")
    innovations = get_filtered_innovations(status=status)
    return render(request, "innovations/innovations_list.html", {"innovations": innovations})


@login_required
def single(request, id):
    try:
        innovation = Innovation.objects.get(id=id)
    except Model.DoesNotExist:
        raise Http404("Page not found!")
    if is_forbidden(innovation.status, request.user):
        raise Http404("Page not found!")
    return render(request, "innovations/innovations_list.html", {"innovations": [innovation]})


@login_required
def set_status(request, id, status):
    if not has_confidential_access(request.user):
        raise render(request, "permission_denied.html")
    innovation = Innovation.objects.get(id=id)
    innovation.status = status
    innovation.save()
    return redirect("single", id=id)


def get_filtered_innovations(**kwargs):
    innovation_query = Innovation.objects.filter(**kwargs)
    return list(innovation_query)


def is_forbidden(status, user):
    return is_confidential(status) and not has_confidential_access(user)


def is_confidential(status):
    return status in [Innovation.Status.BLOCKED, Innovation.Status.PENDING, Innovation.Status.IN_REPLENISHMENT]


def has_confidential_access(user):
    return in_groups(user, [committee_members, administrators])

