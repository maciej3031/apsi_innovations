"""apsi_innovations URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from apsi_innovations.views import users, admin_profile, activate_user, activate_committee

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', include('signup.urls')),
    path(r'innovations/', include('innovations.urls')),
    path(r'accounts/', include('django.contrib.auth.urls')),
    path(r'socials/', include('socials.urls')),
    path(r'users/', users, name='users'),
    path(r'admin_profile/', admin_profile, name='admin_profile'),
    path(r'activate_user/', activate_user, name='activate_user'),
    path(r'activate_committee/', activate_committee, name='activate_committee'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
