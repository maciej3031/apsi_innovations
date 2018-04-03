from django.contrib.auth.models import Group

students, _ = Group.objects.get_or_create(name='students')
employees, _ = Group.objects.get_or_create(name='employees')
committee_members, _ = Group.objects.get_or_create(name='committee_members')
administrators, _ = Group.objects.get_or_create(name='administrators')
