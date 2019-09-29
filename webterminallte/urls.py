"""django_gateone URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from __future__ import absolute_import
from django.conf.urls import url, include
from django.contrib import admin
from webterminallte.views import SshLogPlay, SshTerminalKill, SshTerminalMonitor, SshConnect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.static import serve
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^sshconnect/(?P<ip>(?:(?:0|1[\d]{0,2}|2(?:[0-4]\d?|5[0-5]?|[6-9])?|[3-9]\d?)\.){3}(?:0|1[\d]{0,2}|2(?:[0-4]\d?|5[0-5]?|[6-9])?|[3-9]\d?))/(?P<serverid>[0-9]+)/$',
        SshConnect.as_view(), name='sshconnect'),
    url(r'^sshterminalkill/$', SshTerminalKill.as_view(), name='sshterminalkill'),
    url(r'^sshlogplay/(?P<pk>[0-9]+)/',
        SshLogPlay.as_view(), name='sshlogplay'),
    url(r'^sshterminalmonitor/(?P<pk>[0-9]+)/',
        SshTerminalMonitor.as_view(), name='sshterminalmonitor'),
    url(r'^accounts/login/$',
        LoginView.as_view(template_name='admin/login.html'), name='login'),
    url(r'^accounts/logout/$',
        LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, }),
    ]
