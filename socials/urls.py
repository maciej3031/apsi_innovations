from django.urls import re_path, path

from socials.views import InspirationListView, AddCommentView

urlpatterns = [
    path(r'social_posts/', InspirationListView.as_view(), name='social_posts'),
    re_path(r'^social_posts/(?P<pk>\d+)/comment/$', AddCommentView.as_view(), name='add_comment'),
]
