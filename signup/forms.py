from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from signup.groups import employees, students


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, required=False, help_text='Optional.')

    desired_group = forms.ChoiceField(
        choices=[(group.name, group.name) for group in [students, employees]],
        widget=forms.widgets.RadioSelect()
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)
