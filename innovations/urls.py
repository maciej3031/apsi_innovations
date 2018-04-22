from django.urls import path

from innovations.views import reported, single, set_status

urlpatterns = [
    path('reported/', reported, name='reported'),
    path('single/<int:id>', single, name='single'),
    path('set_status/<int:id>/<str:status>', set_status, name='set_status'),
]
