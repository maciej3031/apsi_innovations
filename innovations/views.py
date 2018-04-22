from django.contrib.auth.decorators import login_required
from django.db.models import Model

from django.shortcuts import render, redirect

from innovations.models import Innovation
from signup.groups import administrators, in_group, committee_members, in_groups


@login_required
def reported(request):
    return render(request, "innovations/innovations_list.html", {"innovations": get_reported_innovations()})


@login_required
def single(request, id):
    try:
        innovation = Innovation.objects.get(id=id)
    except Model.DoesNotExist:
        return render(request, "innovations/innovations_list.html", {"innovations": []})
    innovations = [innovation] if should_be_displayed(innovation, request.user) else []
    return render(request, "innovations/innovations_list.html", {"innovations": innovations})


@login_required
def set_status(request, id, status):
    innovation = Innovation.objects.get(id=id)
    if not in_groups(request.user, [committee_members, administrators]):
        return render(request, "permission_denied.html")
    if (innovation.status == "blocked" or status == "blocked") and not in_group(request.user, administrators):
        return render(request, "permission_denied.html")
    innovation.status = status
    innovation.save()
    return redirect("single", id=id)


def get_reported_innovations():
    Status = Innovation.Status
    innovation_query = Innovation.objects.filter(status__in=[Status.PENDING, Status.SUSPENDED, Status.IN_REPLENISHMENT])
    return list(innovation_query)


def should_be_displayed(innovation, user):
    if innovation.status == Innovation.Status.BLOCKED and not in_group(user, administrators):
        return False  # Only admins can see blocked innovations
    else:
        return True
