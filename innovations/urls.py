from django.urls import path, re_path
from django.views.generic import TemplateView

from innovations.views import single, set_status, InnovationAddView, innovations, my_innovations, appraise, InnovationAppraiseView

urlpatterns = [
    path('', TemplateView.as_view(template_name="innovations/innovations_home.html")),
    re_path('^innovations/', innovations, name='innovations'),
    re_path('^my_innovations/', my_innovations, name='innovations'),
    path('single/<int:id>/', single, name='single'),
    path('set_status/<int:id>/<str:status>/', set_status, name='set_status'),
    path('appraise/<int:id>', InnovationAppraiseView.as_view(), name='appraise'),
    re_path(r'^add_innovation', InnovationAddView.as_view(), name='add_innovation')
]
