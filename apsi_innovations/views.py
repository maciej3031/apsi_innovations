from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction
from signup.groups import administrators, in_group


@login_required
def users(request):
    context = {
        'users': User.objects.all()
    }
    return render(request, "users.html", context)


@login_required
def admin_profile(request):
    if not has_admin_access(request.user):
        return render(request, "permission_denied.html")
    else:
        return render(request, "admin_profile.html")


@login_required
@transaction.atomic
def activate_user(request):
    if not has_admin_access(request.user):
        return render(request, "permission_denied.html")
    else:
        action = request.GET.get("action")
        user = User.objects.get(id=int(request.GET.get("id")))
    if action == "accept":
        user.is_active = True
        user.save()
    elif action == 'block':
        user.is_active = False
        user.save()
    return redirect("users")


@login_required
@transaction.atomic
def activate_committee(request):
    if not has_admin_access(request.user):
        return render(request, "permission_denied.html")
    else:
        action = request.GET.get("action")
        user = User.objects.get(id=int(request.GET.get("id")))
        group = Group.objects.get(name='committee_members')
    if action == "accept":
        user.groups.add(group)
        user.save()
    elif action == 'block':
        user.groups.remove(group)
        user.save()
    return redirect("users")


def has_admin_access(user):
    return in_group(user, administrators)
