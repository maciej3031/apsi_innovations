from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.generic import CreateView, UpdateView, ListView

from innovations.forms import GradeForm, ReportViolationForm, InnovationAddForm, StatusUpdateForm
from innovations.models import Innovation, Keyword, InnovationUrl, InnovationAttachment, Grade, ViolationReport
from innovations.status_flow import try_update_status, available_status_choices
from signup.groups import administrators, committee_members, in_groups, students, in_group, employees


class InnovationAddView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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


class InnovationUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Innovation
    template_name = "add_innovation.html"
    success_url = '/'
    success_message = "%(subject)s was successfully updated"
    fields = ['subject', 'description', 'assumptions', 'benefits', 'costs']

    def dispatch(self, request, *args, **kwargs):
        innovation = get_object_or_404(Innovation, id=kwargs['pk'])
        user_is_not_owner = innovation.issuer != request.user
        replenishment_not_needed = innovation.status != Innovation.Status.IN_REPLENISHMENT
        if user_is_not_owner or replenishment_not_needed:
            return render(request, "permission_denied.html")
        else:
            return super(InnovationUpdateView, self).dispatch(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        form.instance.status = Innovation.Status.PENDING
        form.instance.save()
        return super(InnovationUpdateView, self).form_valid(form)


class ReportViolationView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'innovations/report_violation.html'
    form_class = ReportViolationForm
    success_url = '/'
    success_message = "Violation has been reported. Thank you for your engagement."

    @transaction.atomic
    def form_valid(self, form):
        form.instance.issuer = self.request.user
        form.instance.innovation = Innovation.objects.get(id=self.kwargs['id'])
        return super().form_valid(form)


class InnovationListView(LoginRequiredMixin, ListView):
    paginate_by = 10
    template_name = "innovations/innovations_list.html"
    model = Innovation

    def get_queryset(self):
        queryset = super(InnovationListView, self).get_queryset()
        user = self.request.user
        statuses = self.request.GET.getlist('status')
        if statuses:
            queryset = queryset.filter(status__in=statuses)
        if not has_confidential_access(user):
            queryset = queryset.exclude(status__in=get_confidential_statuses())
        return queryset


@login_required
def details(request, id):
    innovation = get_object_or_404(Innovation, id=id)
    if is_forbidden(innovation.status, request.user):
        raise Http404("Page not found!")
    comments = Grade.objects.filter(innovation=innovation)
    context = {
        'innovation': innovation,
        'comments': comments,
    }
    return render(request, "innovations/details.html", context)


@login_required
@transaction.atomic
def set_status(request, id, status):
    innovation = get_object_or_404(Innovation, id=id)
    try_update_status(request.user, innovation, status)
    return redirect("details", id=id)


@login_required
def vote(request, id):
    innovation = get_object_or_404(Innovation, id=id)
    if get_previous_vote(id, request.user):
        return render(request, "voting_denied.html")
    if has_voting_access(request.user, innovation):
        if request.method == 'GET':
            form = GradeForm()
            return render(request, "innovations/voting.html", {"form": form})
        if request.method == 'POST':
            form = GradeForm(data=request.POST)
            if form.is_valid():
                form.instance.user = request.user
                form.instance.innovation = innovation
                form.instance.save()
            return redirect("details", id=id)
    else:
        return render(request, "permission_denied.html")


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


@login_required
@transaction.atomic
def update_status(request, id):
    innovation = get_object_or_404(Innovation, id=id)
    if request.method == 'GET':
        form = StatusUpdateForm()
        form.fields["status"].choices = available_status_choices(request.user, innovation)
        return render(request, "innovations/update_status.html", {"form": form})
    if request.method == "POST":
        form = StatusUpdateForm(data=request.POST)
        if form.is_valid():
            status = form.cleaned_data.get('status')
            status_substantiation = form.cleaned_data.get('status_substantiation'),
            if try_update_status(request.user, innovation, status, status_substantiation):
                return redirect("details", id=id)
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


def get_previous_vote(innovation_id, user_id):
    try:
        return Grade.objects.get(innovation_id=innovation_id, user_id=user_id)
    except Grade.DoesNotExist:
        return None


def has_voting_access(user, innovation):
    has_voting_status = innovation.status in [Innovation.Status.VOTING]
    has_voting_privileges = (in_group(user, students) and innovation.student_grade_weight) or \
                            (in_group(user, employees) and innovation.employee_grade_weight)
    return has_voting_status and has_voting_privileges
