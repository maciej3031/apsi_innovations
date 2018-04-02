from django.conf.urls import url
from django.contrib.auth.views import login, logout

from signup.views import signup, home, account_inactive

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^account_inactive$', account_inactive, name='account_inactive'),
    url(r'^login/$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', logout, {'next_page': 'login'}, name='logout'),
    url(r'^signup/$', signup, name='signup'),
]
