from django import forms

from innovations.models import Innovation, ViolationReport, Grade


# TODO: url i attachment powinny umożliwiać dodanie więcej niż jednego elementu
class InnovationAddForm(forms.ModelForm):
    keywords = forms.CharField(max_length=2048)
    url = forms.URLField(required=False)
    attachment = forms.FileField(required=False)

    class Meta:
        model = Innovation
        fields = ['subject', 'description', 'benefits', 'costs']


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
