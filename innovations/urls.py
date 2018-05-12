from django.urls import path
from django.views.generic import TemplateView

from innovations.views import single, set_status, InnovationAddView, ReportViolationView, innovations, my_innovations, \
    reported_violations, finish_violation_report, vote

urlpatterns = [
    path('', TemplateView.as_view(template_name="innovations/innovations_home.html")),
    path('innovations/', innovations, name='innovations'),
    path('my_innovations/', my_innovations, name='my_innovations'),
    path('add_innovation/', InnovationAddView.as_view(), name='add_innovation'),
    path('single/<int:id>/', single, name='single'),
    path('set_status/<int:id>/<str:status>/', set_status, name='set_status'),
    path('vote/<int:id>/', vote, name='vote')
    path('report_violation/<int:id>', ReportViolationView.as_view(), name='report_violation'),
    path('reported_violations/', reported_violations, name='reported_violations'),
    path('finish_violation_report/', finish_violation_report, name='finish_violation_report'),
]
