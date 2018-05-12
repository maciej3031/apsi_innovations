from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import Http404

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic import CreateView

from innovations.forms import InnovationAddForm, ReportViolationForm
from innovations.models import Innovation, Keyword, InnovationUrl, InnovationAttachment, ViolationReport
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


@method_decorator(login_required, name='dispatch')
class ReportViolationView(SuccessMessageMixin, CreateView):
    template_name = 'innovations/report_violation.html'
    form_class = ReportViolationForm
    success_url = '/'
    success_message = "Violation has been reported. Thank you for your engagement."

    @transaction.atomic
    def form_valid(self, form):
        form.instance.issuer = self.request.user
        form.instance.innovation = Innovation.objects.get(id=self.kwargs['id'])
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
        return render(request, "permission_denied.html")
    Innovation.objects.get(id=id).update(status=status)
    return redirect("single", id=id)


@login_required
def reported_violations(request):
    if not has_confidential_access(request.user):
        return render(request, "permission_denied.html")
    violations = ViolationReport.objects.filter(closing_date=None)
    return render(request, "innovations/reported_violations.html", {"violations": violations})


@login_required
@transaction.atomic
def finish_violation_report(request):
    if not has_confidential_access(request.user):
        return render(request, "permission_denied.html")
    action = request.GET.get("action")
    violation_report = ViolationReport.objects.get(id=int(request.GET.get("id")))
    if action == "accept":
        violation_report.innovation.status = Innovation.Status.BLOCKED
        violation_report.innovation.save()
    violation_report.closing_date = now()
    violation_report.save()
    return redirect("reported_violations")


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
