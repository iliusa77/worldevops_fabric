from django.conf.urls import patterns, url

# from django.contrib import admin


urlpatterns = patterns('quote.views',

    url(r'^$', 'quote', name='quote'),

    url(r'^home/$', 'quote', name='quote'),

    url(r'^view/$', 'quote_list', name='quote-list'),

    url(r'^success/$', 'success', name='success'),

    url(r'^prev/(?P<cust>[\w|\W]+)/(?P<item>\s+)/$', 'prev', name='prev'),

    url(r'^ajaxloc/(?P<loc>[\w|\W]+)/$', 'getParamsByLocaAjax', name='getParamsByLocaAjax'),

    # url(r'^(?P<qid>\d+)/(?P<status>\w+)/$', 'quote_details', name='quote-details'),

    url(r'^viewed_rfq/(?P<qid>\d+)/(?P<status>\w+)/$', 'viewed_rfq', name='viewed_rfq'),

    url(r'^(?P<qid>\d+)/rfq_generated/$', 'quote_details_rfq_generated', name='rfq_generated'),
	url(r'^(?P<qid>\d+)/response_received/$', 'quote_details_response_received', name='response_received'),
	url(r'^(?P<qid>\d+)/offer_accepted/$', 'quote_details_offer_accepted', name='offer_accepted'),
    url(r'^(?P<qid>\d+)/generate_po/$', 'quote_details_generate_po', name='generate_po'),
	url(r'^(?P<qid>\d+)/po_issued/$', 'quote_details_po_issued', name='po_issued'),
    
    url(r'^(?P<qid>\d+)/counter_price_added/$', 'quote_details_counter_price_added', name='counter_price_added'),
    url(r'^(?P<qid>\d+)/shipped/$', 'quote_details_shipped', name='shipped'),
    url(r'^(?P<qid>\d+)/cancelled_by_user/$', 'quote_details_cancelled_by_user', name='cancelled_by_user'),
    url(r'^(?P<qid>\d+)/counter_response_received/$', 'quote_details_counter_response_received', name='counter_response_received'),
    url(r'^(?P<qid>\d+)/counter_offer_accepted/$', 'quote_details_offer_accepted', name='offer_accepted'),

    url(r'^(?P<qid>\d+)/order_in_production/$', 'quote_details_order_in_production', name='order_in_production'),
    url(r'^(?P<qid>\d+)/order_complete/$', 'quote_details_order_complete', name='order_complete'),


    
)
