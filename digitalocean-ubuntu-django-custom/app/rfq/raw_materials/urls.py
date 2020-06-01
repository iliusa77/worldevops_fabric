from django.conf.urls import patterns, url


urlpatterns = patterns('raw_materials.views',

    url(r'^$', 'date_report', name='date_report'),
    url(r'^date_report/$', 'date_report2', name='date_report2'),


    url(r'^sel_date/$', 'sel_date', name='sel_date'),
    url(r'^add_indian_price2/(?P<date>\d{4}-\d{2}-\d{2})/$', 'add_indian_price2', name='add_indian_price2'),
    url(r'^add_other_price2/(?P<date>\d{4}-\d{2}-\d{2})/(?P<country>\w+)/$', 'add_other_price2', name='add_other_price2'),

    url(r'^make_price/$', 'make_price', name='make_price'),


    url(r'^show_report/(?P<date>\w+)/(?P<country>\d+)/$', 'show_report', name='show_report'),
    url(r'^update_rates/$', 'update_rates', name='update_rates'),

	
	url(r'^get_rmdate/$', 'get_rmdate', name='get_rmdate'),
	url(r'^get_piedate/$', 'get_piedate', name='get_piedate'),

)
