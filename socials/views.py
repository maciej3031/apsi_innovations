from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from socials.forms import SocialPostForm, CommentForm
from socials.models import SocialPost, Comment, SocialPostAttachment


class InspirationListView(LoginRequiredMixin, FormView, ListView):
    context_object_name = 'social_posts'
    form_class = SocialPostForm
    model = SocialPost
    ordering = ["-timestamp"]
    paginate_by = 10
    success_url = '/socials/social_posts/'
    template_name = 'socials/social_posts.html'

    @transaction.atomic
    def form_valid(self, form):
        form.instance.issuer = self.request.user
        form.instance.save()

        for uploaded_file in form.cleaned_data['attachments']:
            SocialPostAttachment.objects.create(file=uploaded_file, social_post=form.instance)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['comment_form'] = CommentForm
        # Hack, for some reason after adding MultiFileField in SocialPostForm, object_list does not exists.
        if not hasattr(self, 'object_list'):
            self.object_list = self.get_queryset()
        return super().get_context_data(**kwargs)


class AddCommentView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    model = Comment
    success_url = '/socials/social_posts/'

    @transaction.atomic
    def form_valid(self, form):
        pk = self.kwargs.get('pk')
        social_post = get_object_or_404(SocialPost, pk=pk)
        form.instance.social_post = social_post
        form.instance.issuer = self.request.user
        self.success_url += str(pk)
        return super().form_valid(form)


@login_required
def single_social_post(request, pk):
    social_post = get_object_or_404(SocialPost, id=pk)
    context = {
        'social_post': social_post,
        'comment_form': CommentForm
    }
    return render(request, "socials/single_social_post.html", context=context)
