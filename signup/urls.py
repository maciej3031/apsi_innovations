from django.contrib.auth.views import login
from django.urls import path

from signup.views import signup, home, account_inactive

urlpatterns = [
    path(r'', home, name='home'),
    path(r'account_inactive/', account_inactive, name='account_inactive'),
    path(r'login/', login, {'template_name': 'login.html'}, name='login'),
    path(r'signup/', signup, name='signup'),
]
