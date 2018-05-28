from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.template import loader
from django.views.generic import CreateView

from innovations.forms import GradeForm, ReportViolationForm, InnovationAddForm, AppraiseForm
from innovations.models import Innovation, Keyword, InnovationUrl, InnovationAttachment, Grade, ViolationReport
from signup.groups import administrators, committee_members, in_groups, students, in_group, employees
from socials.models import Comment, SocialPost


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


class InnovationAppraiseView(SuccessMessageMixin, CreateView):
    template_name = 'innovations/appraise.html'
    form_class = AppraiseForm
    success_url = '/'
    success_message = "You appraised successfully. Thank you!"

    @transaction.atomic
    def form_valid(self, form):
        form.instance.issuer = self.request.user
        form.instance.innovation = Innovation.objects.get(id=self.kwargs['id'])
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
def student_employee_profile(request):
    if not in_groups(request.user, [students, employees]):
        return render(request, "permission_denied.html")
    data = {
        "innovations": Innovation.objects.filter(issuer=request.user),
        "posts": SocialPost.objects.filter(issuer=request.user),
        "comments": Comment.objects.filter(issuer=request.user)
    }
    return render(request, "innovations/student_employee_profile_view.html", data)


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


def calculate_innovation_grade(innovation):
    aggregate_grade = 0
    grades = Grade.objects.get(innovation_id=innovation.id)
    if not grades:
        return None
    number_of_votes = len(grades)
    for grade in grades:
        user_weight = get_user_grade_weight(grade.user_id, innovation)
        aggregate_grade += calculate_single_grade(user_weight, grade.value)
    return aggregate_grade/number_of_votes


def calculate_single_grade(user_weight, user_grade):
    return float(user_weight * user_grade)


def get_user_grade_weight(user, innovation):
    if user.group_id == 1:
        return innovation.student_grade_weight
    elif user.group_id == 3:
        return innovation.employee_grade_weight
    else:
        raise ValueError('Grade given by user without privileges')


@login_required
def single(request, id):
    innovation = get_object_or_404(Innovation, id=id)
    if is_forbidden(innovation.status, request.user):
        raise Http404("Page not found!")
    grade = calculate_innovation_grade(innovation)
    return render(request, "innovations/innovations_list.html", {"innovations": [innovation], "grade": [grade]})


@login_required
def set_status(request, id, status):
    if not has_confidential_access(request.user):
        return render(request, "permission_denied.html")
    Innovation.objects.filter(id=id).update(status=status)
    return redirect("single", id=id)


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
            return redirect("single", id=id)
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
def set_status_substantiation(request, id, status_substantiation):
    if not has_confidential_access(request.user):
        raise render(request, "permission_denied.html")
    Innovation.objects.filter(id=id).update(status_substantiation=status_substantiation)
    return redirect("single", id=id)


def appraise(request, id):
    innovation = get_object_or_404(Innovation, id=id)
    if has_appraise_access(request.user, innovation):
        if request.method == 'GET':
            form = AppraiseForm()
            return render(request, "innovations/appraise.html", {"form": form})
        if request.method == "POST":
            form = AppraiseForm(data=request.POST)
            if form.is_valid():
                Innovation.objects.filter(id=id)\
                    .update(status_substantiation=form.cleaned_data.get('status_substantiation'),
                            status=form.cleaned_data.get('status'))
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


def get_previous_vote(innovation_id, user_id):
    try:
        return Grade.objects.get(innovation_id=innovation_id, user_id=user_id)
    except Grade.DoesNotExist:
        return None


def has_voting_access(user, innovation):
    has_voting_status = innovation.status in [Innovation.Status.VOTING]
    has_voting_privileges = (in_group(user, students) and innovation.student_grade_weight) or \
                            (in_group(user, committee_members) and innovation.employee_grade_weight)
    return has_voting_status and has_voting_privileges


def all_innovation_statuses():
    return [
        getattr(Innovation.Status, status)
        for status in dir(Innovation.Status)
        if isinstance(status, str) and not status.startswith("__")
    ]


def innovation_list(request):
    innovations = Innovation.objects.filter(status='voting').order_by('timestamp')
    suspended = Innovation.objects.filter(status='suspended').order_by('timestamp')
    pending = Innovation.objects.filter(status='pending').order_by('timestamp')
    blocked = Innovation.objects.filter(status='blocked').order_by('timestamp')
    details = Innovation.objects.filter(status='in_replenishment').order_by('timestamp')
    template = loader.get_template('innovation_list.html')
    context = {
        'innovations': innovations,
        'suspended': suspended,
        }
    return HttpResponse(template.render(context, request))


def rejected_list(request):
    rejected = Innovation.objects.filter(status='rejected').order_by('timestamp')
    approved = Innovation.objects.filter(status='accepted').order_by('timestamp')
    template = loader.get_template('closed_list.html')
    context = {
        'rejected': rejected,
        'approved': approved,
        }
    return HttpResponse(template.render(context, request))


def admin_list(request):
    pending = Innovation.objects.filter(status='pending').order_by('timestamp')
    blocked = Innovation.objects.filter(status='blocked').order_by('timestamp')
    details = Innovation.objects.filter(status='IN_REPLENISHMENT').order_by('timestamp')
    template = loader.get_template('admin_list.html')
    context = {
        'blocked': blocked,
        'pending': pending,
        'details': details,
        }
    return HttpResponse(template.render(context, request))


def detail(request, idea_id):
    template = loader.get_template('innovation_detail.html')
    idea = Innovation.objects.filter(id=idea_id)
    comments = Grade.objects.filter(innovation_id=idea_id)
    context = {
        'idea': idea,
        'comments': comments,
    }
    return HttpResponse(template.render(context, request))


def has_appraise_access(user, innovation):
    has_appraise_status = innovation.status in [Innovation.Status.VOTING]
    has_appraise_privileges = (in_groups(user, [committee_members]) and innovation.employee_grade_weight)
    return has_appraise_status and has_appraise_privileges
