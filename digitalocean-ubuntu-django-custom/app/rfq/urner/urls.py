from django.conf.urls import patterns, url


urlpatterns = patterns('urner.views',

    url(r'^$', 'product_add', name='product_add'),
    url(r'^product_add/$', 'product_add', name='product_add'),
    url(r'^product_edit/(?P<cid>\d+)/$', 'product_edit', name='product_edit'),
    url(r'^product_del/(?P<cid>\d+)/$', 'product_del', name='product_del'),

    url(r'^sel_date/$', 'sel_date', name='sel_date'),
    url(r'^product_list/$', 'product_list', name='product_list'),

    url(r'^sel_market_date/$', 'sel_market_date', name='sel_market_date'),

)
