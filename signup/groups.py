from django.contrib.auth.models import Group

students, _ = Group.objects.get_or_create(name='students')
employees, _ = Group.objects.get_or_create(name='employees')
committee_members, _ = Group.objects.get_or_create(name='committee_members')
administrators, _ = Group.objects.get_or_create(name='administrators')


def in_group(user, group):
    return user.groups.filter(name=group.name).exists()


def in_groups(user, groups):
    return any([in_group(user, group) for group in groups])
