from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction
from signup.groups import administrators, in_group, committee_members, in_groups, students, employees
from socials.models import Comment, SocialPost
from innovations.models import Innovation, Grade, InnovationComment


@login_required
def users(request):
    context = {
        'users': User.objects.all()
    }
    return render(request, "users.html", context)


@login_required
def admin_panel(request):
    if not has_admin_access(request.user):
        return render(request, "permission_denied.html")
    else:
        return render(request, "admin_panel.html")


@login_required
@transaction.atomic
def activate_user(request):
    if not has_admin_access(request.user):
        return render(request, "permission_denied.html")
    action = request.GET.get("action")
    user = User.objects.get(id=int(request.GET.get("id")))
    if user == request.user:
        return redirect("users")
    if action == "accept":
        user.is_active = True
        user.save()
    elif action == 'block':
        user.is_active = False
        user.save()
    return redirect("users")


@login_required
def student_employee_profile(request):
    if not in_groups(request.user, [students, employees]):
        return render(request, "permission_denied.html")
    data = {
        "innovations": Innovation.objects.filter(issuer=request.user),
        "posts": SocialPost.objects.filter(issuer=request.user),
        "comments": Comment.objects.filter(issuer=request.user),
        "grades": Grade.objects.filter(user=request.user),
        "innovation_comments": InnovationComment.objects.filter(issuer=request.user)
    }
    return render(request, "student_employee_profile_view.html", data)


@login_required
@transaction.atomic
def activate_committee(request):
    if not has_admin_access(request.user):
        return render(request, "permission_denied.html")
    action = request.GET.get("action")
    user = User.objects.get(id=int(request.GET.get("id")))
    group = committee_members
    if action == "accept":
        user.groups.add(group)
        user.save()
    elif action == 'block':
        user.groups.remove(group)
        user.save()
    return redirect("users")


def has_admin_access(user):
    return in_group(user, administrators)
