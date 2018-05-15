from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect

import sys
if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
    from signup.forms import SignUpForm


@login_required
def home(request):
    return render(request, 'home.html')


def account_inactive(request):
    return render(request, 'registration/account_inactive.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            desired_group = request.POST["desired_group"]
            user = form.save()
            user.is_active = False
            my_group = Group.objects.get(name=desired_group)
            my_group.user_set.add(user)
            user.save()
            return redirect('account_inactive')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
