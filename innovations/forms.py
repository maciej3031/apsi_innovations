from django import forms

from innovations.models import Innovation, ViolationReport, Grade, InnovationComment

# TODO: url i attachment powinny umożliwiać dodanie więcej niż jednego elementu
from innovations.status_flow import available_status_choices


class InnovationAddForm(forms.ModelForm):
    keywords = forms.CharField(max_length=2048)
    url = forms.URLField(required=False)
    attachment = forms.FileField(required=False)

    class Meta:
        model = Innovation
        fields = ['subject', 'description', 'assumptions', 'benefits', 'costs']


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Innovation
        fields = ['status', 'status_substantiation']


class ReportViolationForm(forms.ModelForm):
    class Meta:
        model = ViolationReport
        fields = ['substantiation']


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['value', 'description']


class WeightForm(forms.ModelForm):
    employee_grade_weight = forms.IntegerField(max_value=5, min_value=1)
    student_grade_weight = forms.IntegerField(max_value=5, min_value=1)

    class Meta:
        model = Innovation
        fields = ['student_grade_weight', 'employee_grade_weight']


class InnovationCommentForm(forms.ModelForm):
    text = forms.CharField(label='')

    class Meta:
        model = InnovationComment
        fields = ['text']
