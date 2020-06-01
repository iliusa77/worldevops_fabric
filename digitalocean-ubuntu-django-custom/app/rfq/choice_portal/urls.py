from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'choice_portal.views.home', name='home'),
    # url(r'^quotes/', include('quote.urls')),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('authentication.urls')),
    url(r'^urner/', include('urner.urls')),
    
    url(r'^raw_materials/', include('raw_materials.urls')),

    #url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^$', 'authentication.views.login', name='login'),

    url(r'^home/$', 'authentication.views.home', name='home'),

    #url(r'^home/$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^analytics/$', 'authentication.views.home', name='home'),

    url(r'^quotes/', include('quote.urls')),
    
)
