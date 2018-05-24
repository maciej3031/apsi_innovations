from django.urls import path
from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

from innovations.views import single, set_status, InnovationAddView, ReportViolationView, innovations, my_innovations, \
    reported_violations, finish_violation_report, vote, student_employee_profile

urlpatterns = [
    path('', TemplateView.as_view(template_name="innovations/innovations_home.html")),
    path('innovations/', innovations, name='innovations'),
    path('my_innovations/', my_innovations, name='my_innovations'),
    path('add_innovation/', InnovationAddView.as_view(), name='add_innovation'),
    path('single/<int:id>/', single, name='single'),
    path('set_status/<int:id>/<str:status>/', set_status, name='set_status'),
    path('vote/<int:id>/', vote, name='vote'),
    path('report_violation/<int:id>', ReportViolationView.as_view(), name='report_violation'),
    path('reported_violations/', reported_violations, name='reported_violations'),
    path('finish_violation_report/', finish_violation_report, name='finish_violation_report'),
	url(r'^innovation_list', views.innovation_list, name='innovation_list'),
	url(r'^rejected_list', views.rejected_list, name='rejected_list'),
	url(r'^admin_list', views.admin_list, name='admin_list'),
	url(r'^innovation_details/(?P<idea_id>[0-9]+)', views.detail, name='detail'),
    path('student_employee_profile/', student_employee_profile, name='student_employee_profile'),
    path('edit_innovation/<int:pk>', views.InnovationUpdateView.as_view(), name='edit_innovation'),
]
