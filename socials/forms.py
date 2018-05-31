from django import forms
from multiupload.fields import MultiFileField

from socials.models import SocialPost, Comment


class SocialPostForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, label='')
    attachments = MultiFileField(required=False, max_num=10, max_file_size=1024 * 1024 * 25, label='')

    class Meta:
        model = SocialPost
        fields = ['text']


class CommentForm(forms.ModelForm):
    text = forms.CharField(label='')

    class Meta:
        model = Comment
        fields = ['text']
