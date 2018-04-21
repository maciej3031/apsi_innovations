from django.conf.urls import url

from innovations.views import InnovationAddView

urlpatterns = [
    url(r'^add_innovation', InnovationAddView.as_view(), name='add_innovation'),
]
