from django import forms

from innovations.models import Innovation


# TODO: url i attachment powinny umożliwiać dodanie więcej niż jednego elementu
class InnovationAddForm(forms.ModelForm):
    keywords = forms.CharField(max_length=2048)
    url = forms.URLField()
    attachment = forms.FileField()

    class Meta:
        model = Innovation
        fields = ['subject', 'description', 'benefits', 'costs']
