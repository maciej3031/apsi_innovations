from django.urls import path, re_path
from django.views.generic import TemplateView

from innovations.views import single, set_status, filtered

urlpatterns = [
    path('', TemplateView.as_view(template_name="innovations/innovations_home.html")),
    re_path('^filtered/', filtered, name='filtered'),
    path('single/<int:id>/', single, name='single'),
    path('set_status/<int:id>/<str:status>/', set_status, name='set_status'),
]
