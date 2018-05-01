from django.contrib.auth.decorators import login_required
from django.http import Http404

from django.shortcuts import render, redirect, get_object_or_404

from innovations.models import Innovation
from signup.groups import administrators, committee_members, in_groups


@login_required
def filtered(request):
    owner_id = request.user.id if str(request.user.id) in request.GET.getlist("issuer") else None
    all_statuses = [status.value for status in Innovation.Status]
    kwargs = {"{}__in".format(key): request.GET.getlist(key) for key in request.GET}
    if owner_id:
        kwargs["issuer__in"].remove(str(owner_id))
    kwargs["status__in"] = [
        status for status
        in kwargs.get("status__in", all_statuses)
        if not is_forbidden(status, request.user)
    ]
    innovations = Innovation.objects.filter(**kwargs)
    if owner_id:
        kwargs["status__in"] = request.GET.getlist("status", default=all_statuses)
        kwargs["issuer__in"] = [str(owner_id)]
        innovations |= Innovation.objects.filter(**kwargs)
    return render(request, "innovations/innovations_list.html", {"innovations": innovations})


@login_required
def single(request, id):
    innovation = get_object_or_404(Innovation, id=id)
    if is_forbidden(innovation.status, request.user):
        raise Http404("Page not found!")
    return render(request, "innovations/innovations_list.html", {"innovations": [innovation]})


@login_required
def set_status(request, id, status):
    if not has_confidential_access(request.user):
        raise render(request, "permission_denied.html")
    Innovation.objects.get(id=id).update(status=status)
    return redirect("single", id=id)


def is_forbidden(status, user):
    return is_confidential(status) and not has_confidential_access(user)


def is_confidential(status):
    confidential_statueses = [Innovation.Status.BLOCKED, Innovation.Status.PENDING, Innovation.Status.IN_REPLENISHMENT]
    confidential_statueses += [status.value for status in confidential_statueses]
    return status in confidential_statueses


def has_confidential_access(user):
    return in_groups(user, [committee_members, administrators])
