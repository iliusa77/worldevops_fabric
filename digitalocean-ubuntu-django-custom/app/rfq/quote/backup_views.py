# backup views #

@login_required
def quote_details_response_received_bkup(request, qid):
    quote_item = QuoteItem.objects.get(id=qid)
    if request.POST:
        quoted_price = request.POST["quoted_price"]
        approver_remark = request.POST["remarks"]
        quote_item.quoted_price = quoted_price
        quote_item.approver_remarks = approver_remark
        quote_item.status = 'response_received'
        quote_item.save()
        return HttpResponseRedirect(reverse('quote-list'))
    return render_to_response(
        'quote_details_response_received.html', {'quote_item': quote_item},
        {'quote_item': quote_item},
        context_instance=RequestContext(request))




@login_required
def quote_details_rfq_generated_bkup(request, qid):
    quote_item = QuoteItem.objects.get(id=qid)
    if request.POST:
        quoted_price = request.POST["quoted_price"]
        approver_remark = request.POST["remarks"]
        quote_item.quoted_price = quoted_price
        quote_item.approver_remarks = approver_remark
        quote_item.status = 'response_received'
        quote_item.save()
        return HttpResponseRedirect(reverse('quote-list'))
    return render_to_response(
        'quote_details_rfq_generated.html', {'quote_item': quote_item},        
        context_instance=RequestContext(request))



@login_required
def quote_details_offer_accepted_bkup(request, qid):
    quote_item = QuoteItem.objects.get(id=qid)
    if request.POST:
        quoted_price = request.POST["quoted_price"]
        approver_remark = request.POST["remarks"]
        quote_item.quoted_price = quoted_price
        quote_item.approver_remarks = approver_remark
        quote_item.status = 'response_received'
        quote_item.save()
        return HttpResponseRedirect(reverse('quote-list'))
    return render_to_response(
        'quote_details_offer_accepted.html',
        {'quote_item': quote_item},
        context_instance=RequestContext(request))

@login_required
def quote_details_counter_price_added_bkup(request, qid):
    quote_item = QuoteItem.objects.get(id=qid)
    if request.POST:
        quoted_price = request.POST["quoted_price"]
        approver_remark = request.POST["remarks"]
        quote_item.quoted_price = quoted_price
        quote_item.approver_remarks = approver_remark
        quote_item.status = 'response_received'
        quote_item.save()
        return HttpResponseRedirect(reverse('quote-list'))
    return render_to_response(
        'quote_details_counter_price_added.html',
        {'quote_item': quote_item},
        context_instance=RequestContext(request))

@login_required
def quote_details_generate_PO_bkup(request, qid):
    quote_item = QuoteItem.objects.get(id=qid)
    if request.POST:
        quoted_price = request.POST["quoted_price"]
        approver_remark = request.POST["remarks"]
        quote_item.quoted_price = quoted_price
        quote_item.approver_remarks = approver_remark
        quote_item.status = 'response_received'
        quote_item.save()
        return HttpResponseRedirect(reverse('quote-list'))
    return render_to_response(
        'quote_details_generate_PO.html',
        {'quote_item': quote_item},
        context_instance=RequestContext(request))


@login_required
def quote_details_po_issued_bkup(request, qid):
    quote_item = QuoteItem.objects.get(id=qid)
    if request.POST:
        quoted_price = request.POST["quoted_price"]
        approver_remark = request.POST["remarks"]
        quote_item.quoted_price = quoted_price
        quote_item.approver_remarks = approver_remark
        quote_item.status = 'response_received'
        quote_item.save()
        return HttpResponseRedirect(reverse('quote-list'))
    return render_to_response(
        'quote_details_po_issued.html',
        {'quote_item': quote_item},
        context_instance=RequestContext(request))
            

@login_required
def quote_details_shipped_bkup(request, qid):
    quote_item = QuoteItem.objects.get(id=qid)
    if request.POST:
        quoted_price = request.POST["quoted_price"]
        approver_remark = request.POST["remarks"]
        quote_item.quoted_price = quoted_price
        quote_item.approver_remarks = approver_remark
        quote_item.status = 'response_received'
        quote_item.save()
        return HttpResponseRedirect(reverse('quote-list'))
    return render_to_response(
        'quote_details_shipped.html',
        {'quote_item': quote_item},        
        context_instance=RequestContext(request))

@login_required
def quote_details_cancelled_by_user_bkup(request, qid):
    quote_item = QuoteItem.objects.get(id=qid)
    if request.POST:
        quoted_price = request.POST["quoted_price"]
        approver_remark = request.POST["remarks"]
        quote_item.quoted_price = quoted_price
        quote_item.approver_remarks = approver_remark
        quote_item.status = 'response_received'
        quote_item.save()
        return HttpResponseRedirect(reverse('quote-list'))
    return render_to_response(
        'quote_details_cancelled_by_user.html',
        {'quote_item': quote_item},
        context_instance=RequestContext(request))