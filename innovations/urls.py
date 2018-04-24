from django.urls import path
from django.views.generic import TemplateView

from innovations.views import with_status, single, set_status, my_innovations

urlpatterns = [
    path('', TemplateView.as_view(template_name="innovations/innovations_home.html")),
    path('with_status/<str:status>', with_status, name='with_status'),
    path('my_innovations', my_innovations, name='my_innovations'),
    path('single/<int:id>', single, name='single'),
    path('set_status/<int:id>/<str:status>', set_status, name='set_status'),
]
