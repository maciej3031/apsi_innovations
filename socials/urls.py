from django.conf.urls import url

from socials.views import InspirationListView, AddCommentView

urlpatterns = [
    url(r'^social_posts/$', InspirationListView.as_view(), name='social_posts'),
    url(r'^social_posts/(?P<pk>\d+)/comment/$', AddCommentView.as_view(), name='add_comment'),
]
