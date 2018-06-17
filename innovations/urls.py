from django.urls import path
from django.conf.urls import url
from django.views.generic import TemplateView

from innovations.status_flow import try_finish_status_voting
from . import views

from innovations.views import set_status, InnovationAddView, ReportViolationView, \
    reported_violations, finish_violation_report, vote, update_status, InnovationUpdateView, InnovationListView,\
    update_weights

urlpatterns = [
    path('', TemplateView.as_view(template_name="innovations/innovations_home.html")),
    path('innovations/', InnovationListView.as_view(), name='innovations'),
    path('add_innovation/', InnovationAddView.as_view(), name='add_innovation'),
    path('set_status/<int:id>/<str:status>/', set_status, name='set_status'),
    path('vote/<int:id>/', vote, name='vote'),
    path('report_violation/<int:id>', ReportViolationView.as_view(), name='report_violation'),
    path('reported_violations/', reported_violations, name='reported_violations'),
    path('finish_violation_report/', finish_violation_report, name='finish_violation_report'),
    path('details/<int:id>', views.details, name='details'),
    path('update_status/<int:id>', update_status, name='update_status'),
    path('try_finish_status_voting/<int:id>/', try_finish_status_voting, name='try_finish_status_voting'),
    path('edit_innovation/<int:pk>', InnovationUpdateView.as_view(), name='edit_innovation'),
    path('update_weights/<int:id>/', update_weights, name='update_weights'),
]
