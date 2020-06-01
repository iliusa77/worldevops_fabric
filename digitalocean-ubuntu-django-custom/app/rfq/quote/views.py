from django.shortcuts import render_to_response, HttpResponse, render
from django.views.generic import View
from django.template import RequestContext

from django.core.context_processors import csrf

from django.contrib.auth.decorators import (
    login_required, user_passes_test
)
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib import messages

from django.template import RequestContext  # For CSRF
from django.forms.formsets import formset_factory, BaseFormSet

from .forms import QuoteEntryForm, QuoteItemForm
from .models import *
from userprofile.models import Profile

import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.db.models import Q

#po gen - 

@login_required
def quote(request):

    c={}
    c.update(csrf(request))

    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    QuoteItemFormFormset = formset_factory(QuoteItemForm, max_num=10, formset=RequiredFormSet)
    #QuoteItemFormFormset = formset_factory(QuoteItemForm, max_num=10, formset=BaseFormSet)

    if request.method == "POST":
        data = request.POST.copy()
        # data['requester'] = str(request.user.id)
        # print data
        enrty_form = QuoteEntryForm(data)
        items_formset = QuoteItemFormFormset(request.POST)

        if enrty_form.is_valid() and items_formset.is_valid():

            entry = enrty_form.save()
            entry.status = 'rfq_generated'
            entry.alert = True
            entry.save()

            for form in items_formset.forms:
                item = form.save()
                item.save()
                entry.items.add(item)
                entry.save()

            #return HttpResponseRedirect('/')
            id1 = entry.id
            loc1 = entry.location
            rfqno = 'RFQ/'+ str(loc1) + '/' + str(id1)
            #message = 'RFQ No RFQ/'+ str(loc1) + '/' + str(id1) +' has been generated Succesfully'

            rfq = '<b>'+ str(rfqno) + '</b>'

            message = 'Your Request has been Processed Successfully. Requested Number Is : ' + rfq            
            messages.success(request, message, extra_tags='safe')

            return HttpResponseRedirect(reverse('success'))

            #return render_to_response('message.html', c)
        c['enrty_form'] = enrty_form
        c['items_formset'] = items_formset
        return render(request, 'addQuote.html', c)

    else:

        #usr = str(request.user)
        #user1 = ' '.join([s[0].upper() + s[1:] for s in usr.split('_')]);

        enrty_form = QuoteEntryForm(initial={
            'requester': request.user,
            'item_type' : 'not_sold',
            })
        items_formset = QuoteItemFormFormset()

    c['enrty_form'] = enrty_form
    c['items_formset'] = items_formset


    #return render_to_response('add_quote.html', c)
    return render(request, 'addQuote.html', c) #nj


def success(request):
    c={}
    return render(request, 'message.html', c)




def getParamsByLocaAjax(request, loc):

    c ={}
    k ={}

    obj = LocationRelation.objects.filter(location=loc)

    k ={}
    for i in obj:
        c['id'] = i.id

        c['packer'] = str(i.packer)
        c['packer_id'] = str(int(i.packer.id))

        c['customer'] = str(i.customer)
        c['customer_id'] = str(int(i.customer.id))

        print i.destination

        c['destination'] = str(i.destination)
        c['destination_id'] = str(i.destination.id)

        k = str(k) + "," + str(json.dumps(c))

    print k

    try:
        if len(k) > 0:
            k = k[3:]
            k = "[" + k 
            k = k + "]"
    except Exception, e:
        print e


    return HttpResponse(k, content_type="application/json")


@login_required
def quote_list(request):
    if request.user.is_authenticated():
        quote_items = QuoteInfo.objects.order_by('-id')
        # quote_items = QuoteInfo.objects.all()

        # if request.user.profile.type == Profile.UserTypes.USER:
        #     quote_items = QuoteInfo.objects.filter(requester=request.user)
        if request.user.profile.type == Profile.UserTypes.OTHERUSER:
            quote_items = QuoteInfo.objects.filter(Q(status="generate_po") | Q(status="po_issued") | Q(status="shipped") | Q(status="order_complete") | Q(status="order_in_production"))

        # if request.user.profile.type in [Profile.UserTypes.ADMIN, Profile.UserTypes.ADMINISTRATOR]:
        #     quote_items = QuoteInfo.objects.all()
        # elif request.user.profile.type == Profile.UserTypes.USER:
        #     quote_items = QuoteInfo.objects.filter(quoteinfo__requester=request.user)
        # elif request.user.profile.type == Profile.UserTypes.APPROVER:
        #     quote_items = QuoteInfo.objects.filter(status="offer_accepted")
        # elif request.user.profile.type == Profile.UserTypes.OTHERUSER:
        #     quote_items = QuoteInfo.objects.filter(status="generate_po")


        return render_to_response(
            'quote_list.html', {'quote_items': quote_items},
            context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('login'))



@login_required
def quote_details_rfq_generated(request, qid):

    prev = 0

    quote_info = QuoteInfo.objects.get(id=qid)
    access_flag = True if request.user.profile.type in ['approver', 'admin'] else False
    # access_flag = True if request.user.profile.type in ['admin'] else False


    try:
        it = quote_info.items.all()[0]
        print it.quoted_price
        prev = it.quoted_price
    except Exception, e:
        pass


    if request.POST:
        quote_info.valid_date = request.POST.get("valid_date", None)

        if quote_info.valid_date=='' or quote_info.valid_date=='None':
            quote_info.valid_date = None

        print quote_info.valid_date

        quote_info.alert = True
        quote_info.status = 'response_received'

        remark = request.POST.get("approver_remarks", 'No Remarks')
        quote_info.approver_remarks = remark
        obj = Remarks(rfq=quote_info, from_user=request.user, remark=remark)
        obj.save()

        qprice = request.POST.getlist("quoted_price[]", 0)
        curs = request.POST.getlist("currency[]", 0)

        for i, item in enumerate(quote_info.items.all()):
            item.quoted_price = qprice[i]
            item.currency = curs[i]
            item.save()

        quote_info.save()

        messages.success(request, 'Your Request has been Processed Successfully !!!')
        return HttpResponseRedirect(reverse('quote-list'))
    return render_to_response(
        'quote_details_rfq_generated.html',
        {'quote_item': quote_info, 'access_flag':access_flag, 'prev' : prev},
        context_instance=RequestContext(request))



@login_required
def quote_details_response_received(request, qid):

    quote_info = QuoteInfo.objects.get(id=qid)
    # access_flag = True if request.user.profile.type in ['user'] else False
    access_flag = True if request.user.profile.type in ['user', 'superadmin'] else False

    if request.method == 'POST':

        quote_info.alert = True

        # gp = request.POST.getlist("gross_profit[]", 0.00)
        isp = request.POST.getlist("indication_selling_price[]", [])
        sp = request.POST.getlist("selling_price[]", [])
        co = request.POST.getlist("counter_offer[]", [])

        remark = request.POST.get("requester_remarks", 'No Remarks')
        quote_info.requester_remarks = remark
        obj = Remarks(rfq=quote_info, from_user=request.user, remark=remark)
        obj.save()

        for i, item in enumerate(quote_info.items.all()):

            if isp[i] == '': isp[i] = 0.00
            if sp[i] == '': sp[i] = 0.00
            if co[i] == '': co[i] = 0.00
            # if gp[i] == '': gp[i] = 0.00


            item.indication_selling_price = isp[i]
            item.selling_price = sp[i]
            item.counter_offer = co[i]
            item.save()

        if request.POST.get("accept"):
            quote_info.status = 'offer_accepted'

        elif request.POST.get("counter"):
            quote_info.status = 'counter_price_added'

        elif request.POST.get("reject"):
            quote_info.status = 'cancelled_by_user'

        quote_info.save()
        messages.success(request, 'Your Request has been Processed Successfully !!!')
        return HttpResponseRedirect(reverse('quote-list'))

    return render_to_response(
        'quote_details_response_received.html',
        {'quote_item': quote_info, 'access_flag':access_flag},       
        context_instance=RequestContext(request))



@login_required
def quote_details_offer_accepted(request, qid):
    quote_info = QuoteInfo.objects.get(id=qid)
    access_flag = True if request.user.profile.type in ['approver', 'admin'] else False

    if request.POST:
        quote_info.alert = True
        quote_info.status = 'generate_po'

        remark = request.POST.get("final_approver_remarks", 'No Remarks')
        quote_info.final_approver_remarks = remark
        obj = Remarks(rfq=quote_info, from_user=request.user, remark=remark)
        obj.save()

        dt = request.POST.get("valid_date", None)

        print dt

        if dt=='' or dt=='None':
            dt = None

        quote_info.valid_date = dt




        gp = request.POST.getlist("gross_profit[]", None)

        print gp

        for i, item in enumerate(quote_info.items.all()):

            if gp is not None:
                if len(gp) > i:
                    if gp[i] == '': gp[i] = 0.00

                    item.gross_profit = gp[i]
                    item.save()

        quote_info.save()

        messages.success(request, 'Your Request has been Processed Successfully !!!')
        return HttpResponseRedirect(reverse('quote-list'))

    return render_to_response(
        'quote_details_offer_accepted.html',
        {'quote_item': quote_info, 'access_flag':access_flag},        
        context_instance=RequestContext(request))



@login_required
def quote_details_counter_price_added(request, qid):
    quote_info = QuoteInfo.objects.get(id=qid)
    access_flag = True if request.user.profile.type in ['approver', 'admin'] else False

    if request.POST:
        quote_info.alert = True
        quote_info.status = 'counter_response_received'

        remark = request.POST.get("approver_remarks", 'No Remarks')
        quote_info.approver_remarks = remark
        obj = Remarks(rfq=quote_info, from_user=request.user, remark=remark)
        obj.save()

        fp = request.POST.getlist("final_price[]", 0.00)

        for i, item in enumerate(quote_info.items.all()):
            if fp[i] == '': fp[i] = 0.00
            item.final_price = fp[i]
            item.save()

        quote_info.save()

        messages.success(request, 'Your Request has been Processed Successfully !!!')
        return HttpResponseRedirect(reverse('quote-list'))

    return render_to_response(
        'quote_details_counter_price_added.html',
        {'quote_item': quote_info, 'access_flag':access_flag},        
        context_instance=RequestContext(request))



@login_required
def quote_details_counter_response_received(request, qid):
    quote_info = QuoteInfo.objects.get(id=qid)
    # access_flag = True if request.user.profile.type in ['user'] else False
    access_flag = True if request.user.profile.type in ['user', 'superadmin'] else False

    if request.POST:
        quote_info.alert = True

        if request.POST.get('accept'):
            quote_info.status = 'counter_offer_accepted'
        elif request.POST.get('reject'):
            quote_info.status = 'cancelled_by_user'


        remark = request.POST.get("requester_remarks", 'No Remarks')
        quote_info.requester_remarks = remark
        obj = Remarks(rfq=quote_info, from_user=request.user, remark=remark)
        obj.save()

        co = request.POST.getlist("counter_offer[]", 0.00)

        for i, item in enumerate(quote_info.items.all()):
            if co[i] == '': co[i] = 0.00
            item.final_price = co[i]
            item.save()

        quote_info.save()

        messages.success(request, 'Your Request has been Processed Successfully !!!')
        return HttpResponseRedirect(reverse('quote-list'))

    return render_to_response(
        'quote_details_counter_response_received.html',
        {'quote_item': quote_info, 'access_flag':access_flag},        
        context_instance=RequestContext(request))





@login_required
def quote_details_cancelled_by_user(request, qid):
    quote_info = QuoteInfo.objects.get(id=qid)
    access_flag = True if request.user.profile.type in ['approver', 'admin'] else False

    if request.POST:
        quote_info.alert = True
        quote_info.status = 'cancelled_by_user'

        # remark = request.POST.get("requester_remarks", 'No Remarks')
        # quote_info.requester_remarks = remark
        # obj = Remarks(rfq=quote_info, from_user=request.user, remark=remark)
        # obj.save()

        quote_info.save()

        messages.success(request, 'Your Request has been Processed Successfully !!!')
        return HttpResponseRedirect(reverse('quote-list'))

    return render_to_response(
        'quote_details_cancelled_by_user.html',
        {'quote_item': quote_info, 'access_flag':access_flag},        
        context_instance=RequestContext(request))





@login_required
def quote_details_generate_po(request, qid):
    quote_info = QuoteInfo.objects.get(id=qid)
    access_flag = True if request.user.profile.type in ['otheruser'] else False

    if request.POST:
        quote_info.alert = True
        quote_info.status = 'po_issued'

        # remark = request.POST.get("approver_remarks", 'No Remarks')
        # quote_info.approver_remarks = remark
        # obj = Remarks(rfq=quote_info, from_user=request.user, remark=remark)
        # obj.save()

        quote_info.po = request.POST.get("po", '')        
        quote_info.save()

        messages.success(request, 'Your Request has been Processed Successfully !!!')
        return HttpResponseRedirect(reverse('quote-list'))

    return render_to_response(
        'quote_details_generate_po.html',
        {'quote_item': quote_info, 'access_flag':access_flag},        
        context_instance=RequestContext(request))





@login_required
def quote_details_po_issued(request, qid):
    quote_info = QuoteInfo.objects.get(id=qid)
    # access_flag = True if request.user.profile.type in ['approver', 'superadmin'] else False
    access_flag = True if request.user.profile.type in ['approver', 'superadmin', 'otheruser'] else False

    if request.POST:
        quote_info.alert = True
        quote_info.status = 'order_in_production'

        # remark = request.POST.get("approver_remarks", 'No Remarks')
        # quote_info.approver_remarks = remark
        # obj = Remarks(rfq=quote_info, from_user=request.user, remark=remark)
        # obj.save()

        quote_info.save()        

        messages.success(request, 'Your Request has been Processed Successfully !!!')
        return HttpResponseRedirect(reverse('quote-list'))

    return render_to_response(
        'quote_details_po_issued.html',
        {'quote_item': quote_info, 'access_flag':access_flag},        
        context_instance=RequestContext(request))



@login_required
def quote_details_order_in_production(request, qid):
    quote_info = QuoteInfo.objects.get(id=qid)
    # access_flag = True if request.user.profile.type in ['approver', 'superadmin'] else False
    access_flag = True if request.user.profile.type in ['approver', 'superadmin', 'otheruser'] else False

    if request.POST:
        quote_info.alert = True
        quote_info.status = 'order_complete'

        # remark = request.POST.get("approver_remarks", 'No Remarks')
        # quote_info.approver_remarks = remark
        # obj = Remarks(rfq=quote_info, from_user=request.user, remark=remark)
        # obj.save()

        quote_info.save()        

        messages.success(request, 'Your Request has been Processed Successfully !!!')
        return HttpResponseRedirect(reverse('quote-list'))

    return render_to_response(
        'quote_details_order_in_production.html',
        {'quote_item': quote_info, 'access_flag':access_flag},        
        context_instance=RequestContext(request))




@login_required
def quote_details_order_complete(request, qid):
    quote_info = QuoteInfo.objects.get(id=qid)
    # access_flag = True if request.user.profile.type in ['approver', 'superadmin'] else False
    access_flag = True if request.user.profile.type in ['approver', 'superadmin', 'otheruser'] else False

    if request.POST:
        quote_info.alert = True
        quote_info.status = 'shipped'

        # remark = request.POST.get("approver_remarks", 'No Remarks')
        # quote_info.approver_remarks = remark
        # obj = Remarks(rfq=quote_info, from_user=request.user, remark=remark)
        # obj.save()

        quote_info.container_number = request.POST.get("container_number", '')      
        quote_info.save()

        messages.success(request, 'Your Request has been Processed Successfully !!!')
        return HttpResponseRedirect(reverse('quote-list'))

    return render_to_response(
        'quote_details_order_complete.html',
        {'quote_item': quote_info, 'access_flag':access_flag},        
        context_instance=RequestContext(request))





@login_required
def quote_details_shipped(request, qid):
    quote_info = QuoteInfo.objects.get(id=qid)

    return render_to_response(
        'quote_details_shipped.html',
        {'quote_item': quote_info},        
        context_instance=RequestContext(request))





def viewed_rfq(request, qid, status):

    print qid, status, request.user.profile.type

    alert_flag = whoami(request, status)

    quote_info = QuoteInfo.objects.get(id=qid)
    quote_info.alert = alert_flag
    quote_info.save()

    return HttpResponseRedirect('/quotes/'+qid+"/"+status+"/")



def whoami(request, status):

    alert_flag=True
    if status == "rfq_generated":
        alert_flag = False if request.user.profile.type in ['approver', 'admin'] else True
    elif status == "response_received":
        alert_flag = False if request.user.profile.type in ['user'] else True
    elif status == "offer_accepted":
        alert_flag = False if request.user.profile.type in ['approver', 'admin'] else True
    elif status == "counter_price_added":
        alert_flag = False if request.user.profile.type in ['approver', 'admin'] else True
    elif status == "generate_po":
        alert_flag = False if request.user.profile.type in ['otheruser'] else True
    elif status == "po_issued":
        alert_flag = False if request.user.profile.type in ['approver', 'admin', 'superadmin'] else True
    elif status == "cancelled_by_user":
        alert_flag = False if request.user.profile.type in ['approver', 'admin'] else True
    elif status == "counter_response_received":
        alert_flag = False if request.user.profile.type in ['user'] else True

    elif status == "order_in_production":
        alert_flag = False if request.user.profile.type in ['approver', 'admin', 'superadmin', 'otheruser'] else True
    elif status == "order_complete":
        alert_flag = False if request.user.profile.type in ['approver', 'superadmin', 'admin', 'otheruser'] else True
    elif status == "shipped":
        alert_flag = False if request.user.profile.type in ['approver', 'superadmin', 'admin', 'otheruser'] else True

    elif status == "counter_offer_accepted":
        alert_flag = False if request.user.profile.type in ['approver', 'admin'] else True

    return alert_flag



def whoami_bkup(request, status):

    alert_flag=False
    if status == "rfq_generated":
        alert_flag = True if request.user.profile.type in ['approver', 'admin'] else False
    elif status == "response_received":
        alert_flag = True if request.user.profile.type in ['user'] else False
    elif status == "offer_accepted":
        alert_flag = True if request.user.profile.type in ['approver', 'admin'] else False
    elif status == "counter_price_added":
        alert_flag = True if request.user.profile.type in ['approver', 'admin'] else False
    elif status == "generate_po":
        alert_flag = True if request.user.profile.type in ['superadmin'] else False
    elif status == "po_issued":
        alert_flag = True if request.user.profile.type in ['otheruser'] else False
    elif status == "cancelled_by_user":
        alert_flag = True if request.user.profile.type in ['approver', 'admin'] else False
    elif status == "counter_response_received":
        alert_flag = True if request.user.profile.type in ['user'] else False

    elif status == "order_in_production":
        alert_flag = True if request.user.profile.type in ['otheruser'] else False
    elif status == "order_complete":
        alert_flag = True if request.user.profile.type in ['otheruser'] else False
    elif status == "shipped":
        alert_flag = True if request.user.profile.type in ['approver', 'admin'] else False

    elif status == "counter_offer_accepted":
        alert_flag = True if request.user.profile.type in ['approver', 'admin'] else False

    return alert_flag



def prev(request, cust, item):

    data = ''

    cust = '1'
    item = '1'

    try:
        obj = QuoteInfo.objects.filter(items=item, customer=cust)[0:]
        for i in obj:
            x = i.items

        #ob1 = obj[0:].items

    except Exception, e:
        raise e
    
    ob1 = {'item' : 'cpto', 'price' : '10'}

    #data = serializers.serialize("json", ob1)
    #return HttpResponse(qry.as_dict())
    return HttpResponse(json.dumps(ob1))


