from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
        url(r'^$', views.app_index, name='app_index'),
        url(r'^(?P<app_name>[^/]+)/$', views.app_settings, name='app_settings'),
        url(r'^(?P<app_name>[^/]+)/(?P<group_name>[^/]+)/$', views.app_group_settings, name='app_group_settings'),
    )

# vim: et sw=4 sts=4
