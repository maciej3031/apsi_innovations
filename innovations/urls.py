from django.urls import path, re_path
from django.views.generic import TemplateView

from innovations.views import single, set_status, InnovationAddView, ReportViolationView, innovations, my_innovations, \
    reported_violations, finish_violation_report

urlpatterns = [
    path('', TemplateView.as_view(template_name="innovations/innovations_home.html")),
    re_path('^innovations/', innovations, name='innovations'),
    re_path('^my_innovations/', my_innovations, name='my_innovations'),
    re_path(r'^add_innovation', InnovationAddView.as_view(), name='add_innovation'),
    path('single/<int:id>/', single, name='single'),
    path('set_status/<int:id>/<str:status>/', set_status, name='set_status'),
    path('report_violation/<int:id>', ReportViolationView.as_view(), name='report_violation'),
    path('reported_violations/', reported_violations, name='reported_violations'),
    path('finish_violation_report/', finish_violation_report, name='finish_violation_report'),
]
