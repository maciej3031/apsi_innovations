from django import forms

from innovations.models import Innovation, ViolationReport


# TODO: url i attachment powinny umożliwiać dodanie więcej niż jednego elementu
class InnovationAddForm(forms.ModelForm):
    keywords = forms.CharField(max_length=2048)
    url = forms.URLField()
    attachment = forms.FileField()

    class Meta:
        model = Innovation
        fields = ['subject', 'description', 'benefits', 'costs']


class ReportViolationForm(forms.ModelForm):
    class Meta:
        model = ViolationReport
        fields = ['substantiation']