from django.conf.urls import patterns, include, url
from django.conf import settings
from authentication.views import *
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('authentication.views',
	
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout1, name='logout1'),

    url(r'^backup/$', dbbackup, name='dbbackup'),
    
)
