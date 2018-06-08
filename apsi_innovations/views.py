from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def users(request):
    context = {
        'users': User.objects.all()
    }
    return render(request, "users.html", context)
