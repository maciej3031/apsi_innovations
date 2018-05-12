from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import Http404

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView

from innovations.forms import InnovationAddForm, AppraiseForm
from innovations.models import Innovation, Keyword, InnovationUrl, InnovationAttachment
from signup.groups import administrators, committee_members, in_groups


class InnovationAddView(SuccessMessageMixin, CreateView):
    template_name = 'add_innovation.html'
    form_class = InnovationAddForm
    success_url = '/'
    success_message = "%(subject)s was created successfully"

    @transaction.atomic
    def form_valid(self, form):
        form.instance.issuer = self.request.user
        form.instance.save()

        keywords = [Keyword(keyword=x.strip(), innovation=form.instance) for x in
                    form.cleaned_data['keywords'].split(',')]
        Keyword.objects.bulk_create(keywords)

        InnovationUrl.objects.create(url=form.cleaned_data['url'], innovation=form.instance)
        InnovationAttachment.objects.create(file=form.cleaned_data['attachment'], innovation=form.instance)

        return super().form_valid(form)


@login_required
def my_innovations(request):
    innovations = Innovation.objects.filter(issuer=request.user)
    status = request.GET.get('status')
    if status is not None:
        innovations = innovations.filter(status=status)
    return render(request, "innovations/innovations_list.html", {"innovations": innovations})


@login_required
def innovations(request):
    user = request.user
    innovations = Innovation.objects.all()
    status = request.GET.get('status')
    if status is not None:
        innovations = innovations.filter(status=status)
    if not has_confidential_access(user):
        innovations = innovations.exclude(status__in=get_confidential_statuses())
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


@login_required
def set_status_substantiation(request, id, status_substantiation):
    if not has_confidential_access(request.user):
        raise render(request, "permission_denied.html")
    Innovation.objects.get(id=id).update(status_substantiation=status_substantiation)
    return redirect("single", id=id)


@login_required
def appraise(request, id):
    innovation = get_object_or_404(Innovation, id=id)
    if has_appraise_access(request.user, innovation):
        if request.method == 'GET':
            form = AppraiseForm()
            return render(request, "innovations/appraise.html", {"form": form})
        if request.method == "POST":
            form = AppraiseForm(data=request.POST)
            if form.is_valid():
                Innovation.status = set_status(request, id, form.cleaned_data.get('status'))
                Innovation.status_substantiation = \
                    set_status_substantiation(request, id, form.cleaned_data.get('status_substantiation'))
            return redirect("single", id=id)
    else:
        return render(request, "permission_denied.html")


def is_forbidden(status, user):
    return is_confidential(status) and not has_confidential_access(user)


def is_confidential(status):
    return status in get_confidential_statuses()


def get_confidential_statuses():
    return [Innovation.Status.BLOCKED, Innovation.Status.PENDING, Innovation.Status.IN_REPLENISHMENT]


def has_confidential_access(user):
    return in_groups(user, [committee_members, administrators])


def all_innovation_statuses():
    return [
        getattr(Innovation.Status, status)
        for status in dir(Innovation.Status)
        if isinstance(status, str) and not status.startswith("__")
    ]


def has_appraise_access(user, innovation):
    has_appraise_status = innovation.status in [Innovation.Status.VOTING]
    has_appraise_privileges = (in_groups(user, [committee_members]) and innovation.employee_grade_weight)
    return has_appraise_status and has_appraise_privileges
