from django.shortcuts import render_to_response, HttpResponse, render
from django.views.generic import View
from django.template import RequestContext

from django.core.context_processors import csrf

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.template import RequestContext  # For CSRF
from django.forms.formsets import formset_factory, BaseFormSet

from .models import *

from django.contrib import messages

from django.contrib.auth.decorators import (
    login_required, user_passes_test
)

# Create your views here.


#========================================= urner ====================================

@login_required
def product_add(request):

	if request.method == 'POST':
		name =  request.POST.get('name', '')
		obj = Product(name=name)
		obj.save()

		messages.success(request, 'Save Successful')

		return HttpResponseRedirect(reverse('product_add'))

	else:
		c={}
		c.update(csrf(request))

		cats = Product.objects.all()
		c['cats'] = cats

		return render(request, 'addProduct.html', c)


@login_required
def product_edit(request, cid):

	if request.method == 'POST':
		name =  request.POST.get('name', '')

		obj = Product.objects.get(pk=cid)
		obj.name = name
		obj.save()

		messages.success(request, 'Save Successful')

		return HttpResponseRedirect(reverse('product_add'))

	else:
		c={}
		c.update(csrf(request))

		sel = Product.objects.get(pk=cid)
		c['sel'] = sel
		c['cid'] = cid

		return render(request, 'editProduct.html', c)

@login_required
def product_del(request, cid):

	try:
		Product.objects.get(pk=cid).delete()
		messages.success(request, 'Deleted Successfully')
	except Exception, e:
		messages.success(request, 'Error in Deletion!')

	return HttpResponseRedirect(reverse('product_add'))


@login_required
def sel_date(request):

	c={}
	c.update(csrf(request))

	if request.method == 'POST':
		date = request.POST.get('date', None)
		c['date'] = date

 		c['cats'] = Product.objects.all()

		return render(request, 'listProduct.html', c)

	else:

		return render(request, 'dateProductPrice.html', c)



@login_required
def product_list(request):

	if request.method == 'POST':

		count = request.POST.get('count', None)
		date = request.POST.get('date', None)

		if count is not None:
			count = int(count)

			i=0
			while (i<count):
				i = i + 1	
				pid = request.POST.get("pdt"+str(i), "-1")
				pprice = request.POST.get("price"+str(i), "-1")
				
				pid = int(pid)
				if pid != -1 and pprice != -1:
					pdt = Product.objects.get(pk=pid)
					obj = ProductDetails(product=pdt, price=pprice, date=date)
					obj.save()

		messages.success(request, 'Saved Successfully')

		return HttpResponseRedirect('/')			

	else:
		return HttpResponseRedirect(reverse('date_report'))



@login_required
def sel_market_date(request):

	c={}
	c.update(csrf(request))

	if request.method == 'POST':

		pdt = request.POST.get('pdt', None)
		sdate = request.POST.get('sdate', None)
		edate = request.POST.get('edate', None)

		print pdt

		try:
			if pdt == '-1':

				product_details = ProductDetails.objects.filter(date__range=(sdate, edate))
				products = [Product.objects.get(id=id) for id in product_details.values_list('product',flat=True).distinct()]
				date_list = ProductDetails.objects.values_list('date',flat=True).distinct().order_by('date')
				data_dict = {}

				for p in products:
				    data_dict[p] = []
				    for date in date_list:
				        pd = ProductDetails.objects.filter(date=date, product=p)
				        if pd:
				            data_dict[p].append(pd[0].price)
				        else:
				            data_dict[p].append(0)

				c['data_dict'] = data_dict
				c['date_list'] = date_list

				print products

				return render(request, 'showReport2.html', c)
			else:
				product = Product.objects.get(id=pdt)
				c['product'] = product		
 				c['cats'] = ProductDetails.objects.filter(date__range=(sdate, edate), product=product)

 				return render(request, 'showReport.html', c)

		except Product.DoesNotExist:
			message = "<font color='red'>Please Select Product</font>"
			messages.success(request, message, extra_tags='safe')
			return HttpResponseRedirect(reverse('sel_market_date'))

		return render(request, 'showReport.html', c)

	else:

		c['cat'] = Product.objects.all()

		return render(request, 'selectReport.html', c)



@login_required
def sel_market_date2(request):

	c={}
	c.update(csrf(request))

	if request.method == 'POST':

		pdt = request.POST.get('pdt', None)
		sdate = request.POST.get('sdate', None)
		edate = request.POST.get('edate', None)

		print pdt

		# try:
		# 	product = Product.objects.get(id=pdt)
		# 	c['product'] = product		
 	# 		c['cats'] = ProductDetails.objects.filter(date__range=(sdate, edate), product=product)
 			
		# except Product.DoesNotExist:
		# 	message = "<font color='red'>Please Select Product</font>"
		# 	messages.success(request, message, extra_tags='safe')
		# 	return HttpResponseRedirect(reverse('sel_market_date'))

		try:
			if pdt == '-1':
				c['cats'] = ProductDetails.objects.filter(date__range=(sdate, edate))

				return render(request, 'showReport2.html', c)
			else:
				product = Product.objects.get(id=pdt)
				c['product'] = product		
 				c['cats'] = ProductDetails.objects.filter(date__range=(sdate, edate), product=product)

 				return render(request, 'showReport.html', c)

		except Product.DoesNotExist:
			raise e

		return render(request, 'showReport.html', c)

	else:

		c['cat'] = Product.objects.all()

		return render(request, 'selectReport.html', c)

#======================================== urner ====================================




@login_required
def sel_market_date1(request):

	c={}
	c.update(csrf(request))

	if request.method == 'POST':

		pdt = request.POST.get('pdt', None)
		sdate = request.POST.get('sdate', None)
		edate = request.POST.get('edate', None)

		product_details = ProductDetails.objects.filter(date__range=(sdate, edate))
		products = [Product.objects.get(id=id) for id in product_details.values_list('product',flat=True).distinct()]
		date_list = ProductDetails.objects.values_list('date',flat=True).distinct().order_by('date')
		data_dict = {}

		for p in products:
		    data_dict[p] = []
		    for date in date_list:
		        pd = ProductDetails.objects.filter(date=date, product=p)
		        if pd:
		            data_dict[p].append(pd[0].price)
		        else:
		            data_dict[p].append(0)

		c['data_dict'] = data_dict
		c['date_list'] = date_list

		print products




		return render(request, 'showReport2.html', c)

	else:

		c['cat'] = Product.objects.all()

		return render(request, 'selectReport.html', c)