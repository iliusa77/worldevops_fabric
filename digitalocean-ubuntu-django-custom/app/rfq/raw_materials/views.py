from django.shortcuts import render_to_response, HttpResponse, render
from django.views.generic import View
from django.template import RequestContext

from django.core.context_processors import csrf

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.template import RequestContext  # For CSRF
from django.forms.formsets import formset_factory, BaseFormSet

from .models import *

from urner.models import *
from quote.models import *

from django.contrib import messages

from django.contrib.auth.decorators import (
    login_required, user_passes_test
)


import json, urllib, urllib2
import datetime
from datetime import date, datetime, timedelta
import itertools
import ast

import collections
import operator
# Create your views here.


#========================================= rm ====================================

@login_required
def sel_date(request):

	c={}
	c.update(csrf(request))

	if request.method == 'POST':
		date = request.POST.get('date', None)
		country =  request.POST.get('country', None)

		c['date'] = date
		c['country'] = country

		#return HttpResponse(country)

		if country is not None and date is not None:
			if country == 'india':
				return HttpResponseRedirect('/raw_materials/add_indian_price2/'+date+'/')
			else:
				return HttpResponseRedirect('/raw_materials/add_other_price2/'+date+'/'+country+'/')
		else:
			messages.success(request, 'Error In Values')
			return HttpResponseRedirect(reverse('sel_date'))

	else:

		c['cats'] = Product.objects.all()
		return render(request, 'rm_price_entry.html', c)




@login_required
def add_indian_price(request, date):

	c = {}
	c.update(csrf(request))
	c['size'] = Size.objects.all()
	c['hide'] = True

	if request.method == 'POST':
		c = {}
		c.update(csrf(request))

		c['size'] = Size.objects.all()

		if request.method == 'POST':

			count = request.POST.get('count', None)

			count = int(count)

			i=0
			while (i<count):
				i = i + 1
				size = request.POST.get('size'+str(i), None)

				if size is not None:
					size = Size.objects.get(size=size)

					cpto = request.POST.get('cpto'+str(i), None)
					item = Item.objects.get(name='cpto')
					yld = Yields.objects.get(item=item)
					obj = OtherPrice(yields = yld, size = size, price=cpto, date=date, country="india")
					obj.save()

					rpto = request.POST.get('rpto'+str(i), None)
					item = Item.objects.get(name='rpto')
					yld = Yields.objects.get(item=item)
					obj = OtherPrice(yields = yld, size = size, price=rpto, date=date, country="india")
					obj.save()

					ezpl = request.POST.get('ezpl'+str(i), None)
					item = Item.objects.get(name='ezpl')
					yld = Yields.objects.get(item=item)
					obj = OtherPrice(yields = yld, size = size, price=ezpl, date=date, country="india")
					obj.save()

					cpnd = request.POST.get('cpnd'+str(i), None)
					item = Item.objects.get(name='cpnd')
					yld = Yields.objects.get(item=item)
					obj = OtherPrice(yields = yld, size = size, price=cpnd, date=date, country="india")
					obj.save()

					rpnd = request.POST.get('rpnd'+str(i), None)
					item = Item.objects.get(name='rpnd')
					yld = Yields.objects.get(item=item)
					obj = OtherPrice(yields = yld, size = size, price=rpnd, date=date, country="india")
					obj.save()

		
		messages.success(request, 'Save Successful')
		return HttpResponseRedirect('/')

	else:

		return render(request, 'addIndianPrice.html', c)



@login_required
def add_indian_price2(request, date):

	c = {}
	c.update(csrf(request))
	c['size'] = Size.objects.all()
	c['hide'] = True
	c['date'] = date

	if request.method == 'POST':
		c = {}
		c.update(csrf(request))

		c['size'] = Size.objects.all()
		c['date'] = date

		if request.method == 'POST':

			count = request.POST.get('count', None)

			count = int(count)

			i=0
			while (i<count):
				i = i + 1
				size = request.POST.get('size'+str(i), None)

				if size is not None:
					size = Size.objects.get(size=size)

					cpto = request.POST.get('cpto'+str(i), None)
					item = Item.objects.get(name='cpto')
					yld = Yields.objects.get(item=item)

					try:
						obj = RmPrice.objects.get(yields = yld, date=date, size = size)
						obj.india = cpto
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, india = cpto, date=date)

					obj.save()

					rpto = request.POST.get('rpto'+str(i), None)
					item = Item.objects.get(name='rpto')
					yld = Yields.objects.get(item=item)

					try:
						obj = RmPrice.objects.get(yields = yld, date=date, size = size)
						obj.india = rpto
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, india = rpto, date=date)

					obj.save()

					ezpl = request.POST.get('ezpl'+str(i), None)
					item = Item.objects.get(name='ezpl')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = RmPrice.objects.get(yields = yld, date=date, size = size)
						obj.india = ezpl
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, india = ezpl, date=date)

					obj.save()

					cpnd = request.POST.get('cpnd'+str(i), None)
					item = Item.objects.get(name='cpnd')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = RmPrice.objects.get(yields = yld, date=date, size = size)
						obj.india = cpnd
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, india = cpnd, date=date)

					obj.save()

					rpnd = request.POST.get('rpnd'+str(i), None)
					item = Item.objects.get(name='rpnd')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = RmPrice.objects.get(yields = yld, date=date, size = size)
						obj.india = rpnd
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, india = rpnd, date=date)

					obj.save()

		
		messages.success(request, 'Save Successful')

		return HttpResponseRedirect('/')

	else:

		#return render(request, 'addIndianPrice1.html', c)
		return render(request, 'addIndianPrice.html', c)


@login_required
def add_other_price2(request, date, country):

	c = {}
	c.update(csrf(request))

	c['size'] = Size.objects.all()
	c['country'] = country
	c['date'] = date

	if request.method == 'POST':

		count = request.POST.get('count', None)

		count = int(count)

		i=0
		while (i<count):
			i = i + 1
			size = request.POST.get('size'+str(i), None)
			
			if size is not None:
				size = Size.objects.get(size=size)

				ok1 = RmPrice.objects.filter(date=date, size = size)
				

				if country == 'indonesia':
					cpto = request.POST.get('cpto'+str(i), None)
					item = Item.objects.get(name='cpto')
					yld = Yields.objects.get(item=item)

					try:
						obj = RmPrice.objects.get(yields = yld, date=date, size = size)
						obj.indonesia = cpto
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, indonesia = cpto, date=date)

					obj.save()

					rpto = request.POST.get('rpto'+str(i), None)
					item = Item.objects.get(name='rpto')
					yld = Yields.objects.get(item=item)

					try:
						obj = RmPrice.objects.get(yields = yld, date=date, size = size)
						obj.indonesia = rpto
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, indonesia = rpto, date=date)

					obj.save()

					ezpl = request.POST.get('ezpl'+str(i), None)
					item = Item.objects.get(name='ezpl')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = RmPrice.objects.get(yields = yld, date=date, size = size)
						obj.indonesia = ezpl
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, indonesia = ezpl, date=date)

					obj.save()

					cpnd = request.POST.get('cpnd'+str(i), None)
					item = Item.objects.get(name='cpnd')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = RmPrice.objects.get(yields = yld, date=date, size = size)
						obj.indonesia = cpnd
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, indonesia = cpnd, date=date)

					obj.save()

					rpnd = request.POST.get('rpnd'+str(i), None)
					item = Item.objects.get(name='rpnd')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = RmPrice.objects.get(yields = yld, date=date, size = size)
						obj.indonesia = rpnd
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, indonesia = rpnd, date=date)

					obj.save()


				elif country == 'thailand':
					cpto = request.POST.get('cpto'+str(i), None)
					item = Item.objects.get(name='cpto')
					yld = Yields.objects.get(item=item)

					try:
						obj = ok1.get(yields = yld)
						obj.thailand = cpto
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, thailand = cpto, date=date)

					obj.save()

					rpto = request.POST.get('rpto'+str(i), None)
					item = Item.objects.get(name='rpto')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.thailand = rpto
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, thailand = rpto, date=date)

					obj.save()

					ezpl = request.POST.get('ezpl'+str(i), None)
					item = Item.objects.get(name='ezpl')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.thailand = ezpl
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, thailand = ezpl, date=date)

					obj.save()

					cpnd = request.POST.get('cpnd'+str(i), None)
					item = Item.objects.get(name='cpnd')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.thailand = cpnd
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, thailand = cpnd, date=date)

					obj.save()

					rpnd = request.POST.get('rpnd'+str(i), None)
					item = Item.objects.get(name='rpnd')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.thailand = rpnd
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, thailand = rpnd, date=date)

					obj.save()


				elif country == 'vietnam':
					cpto = request.POST.get('cpto'+str(i), None)
					item = Item.objects.get(name='cpto')
					yld = Yields.objects.get(item=item)

					try:
						obj = ok1.get(yields = yld)
						obj.vietnam = cpto
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, vietnam = cpto, date=date)

					obj.save()

					rpto = request.POST.get('rpto'+str(i), None)
					item = Item.objects.get(name='rpto')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.vietnam = rpto
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, vietnam = rpto, date=date)

					obj.save()

					ezpl = request.POST.get('ezpl'+str(i), None)
					item = Item.objects.get(name='ezpl')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.vietnam = ezpl
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, vietnam = ezpl, date=date)

					obj.save()

					cpnd = request.POST.get('cpnd'+str(i), None)
					item = Item.objects.get(name='cpnd')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.vietnam = cpnd
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, vietnam = cpnd, date=date)

					obj.save()

					rpnd = request.POST.get('rpnd'+str(i), None)
					item = Item.objects.get(name='rpnd')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.vietnam = rpnd
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, vietnam = rpnd, date=date)

					obj.save()


				elif country == 'India_other':
					cpto = request.POST.get('cpto'+str(i), None)
					item = Item.objects.get(name='cpto')
					yld = Yields.objects.get(item=item)

					try:
						obj = ok1.get(yields = yld)
						obj.india_other = cpto
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, india_other = cpto, date=date)

					obj.save()

					rpto = request.POST.get('rpto'+str(i), None)
					item = Item.objects.get(name='rpto')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.india_other = rpto
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, india_other = rpto, date=date)

					obj.save()

					ezpl = request.POST.get('ezpl'+str(i), None)
					item = Item.objects.get(name='ezpl')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.india_other = ezpl
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, india_other = ezpl, date=date)

					obj.save()

					cpnd = request.POST.get('cpnd'+str(i), None)
					item = Item.objects.get(name='cpnd')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.india_other = cpnd
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, india_other = cpnd, date=date)

					obj.save()

					rpnd = request.POST.get('rpnd'+str(i), None)
					item = Item.objects.get(name='rpnd')
					yld = Yields.objects.get(item=item)
					
					try:
						obj = ok1.get(yields = yld)
						obj.india_other = rpnd
					except Exception, e:
						obj = RmPrice(yields = yld, size = size, india_other = rpnd, date=date)

					obj.save()
					



		messages.success(request, 'Save Successful')

		return HttpResponseRedirect('/')

	else:

		return render(request, 'rm_indo_price.html', c)



@login_required
def add_other_price(request, date, country):

	c = {}
	c.update(csrf(request))

	c['size'] = Size.objects.all()
	c['country'] = country

	if request.method == 'POST':

		count = request.POST.get('count', None)

		count = int(count)

		i=0
		while (i<count):
			i = i + 1
			size = request.POST.get('size'+str(i), None)
			
			if size is not None:
				size = Size.objects.get(size=size)

				cpto = request.POST.get('cpto'+str(i), None)
				item = Item.objects.get(name='cpto')
				yld = Yields.objects.get(item=item)
				obj = OtherPrice(yields = yld, size = size, price=cpto, date=date, country=country)
				obj.save()

				rpto = request.POST.get('rpto'+str(i), None)
				item = Item.objects.get(name='rpto')
				yld = Yields.objects.get(item=item)
				obj = OtherPrice(yields = yld, size = size, price=rpto, date=date, country=country)
				obj.save()

				ezpl = request.POST.get('ezpl'+str(i), None)
				item = Item.objects.get(name='ezpl')
				yld = Yields.objects.get(item=item)
				obj = OtherPrice(yields = yld, size = size, price=ezpl, date=date, country=country)
				obj.save()

				cpnd = request.POST.get('cpnd'+str(i), None)
				item = Item.objects.get(name='cpnd')
				yld = Yields.objects.get(item=item)
				obj = OtherPrice(yields = yld, size = size, price=cpnd, date=date, country=country)
				obj.save()

				rpnd = request.POST.get('rpnd'+str(i), None)
				item = Item.objects.get(name='rpnd')
				yld = Yields.objects.get(item=item)
				obj = OtherPrice(yields = yld, size = size, price=rpnd, date=date, country=country)
				obj.save()

		messages.success(request, 'Save Successful')

		return HttpResponseRedirect('/')

	else:

		return render(request, 'rm_indo_price.html', c)



@login_required
def update_rates(request):

	c = {}
	c.update(csrf(request))

	if request.method == 'POST':
		rate = request.POST.get('rate', '')
		exp = request.POST.get('exp', '')

		try:
			obj = Rates.objects.all()[:0]
			obj.rate = rate
			obj.exp = exp

		except Exception, e:
			obj = Rates(rate=rate, exp=exp)

		obj.save()

		messages.success(request, 'Updated Values!')
		return HttpResponseRedirect(reverse('product_add'))


@login_required
def date_report2(request):
	c={}
	c.update(csrf(request))

	if request.method == 'POST':
		date = request.POST.get('date', None)
		pdt = request.POST.get('pdt', None)

		try:
			item = Item.objects.get(id=pdt)
			pdt = Yields.objects.get(item=item)
		except Exception, e:
			pass


		c['cats'] = RmPrice.objects.filter(date=date , yields=pdt)

		return render(request, 'rm_price.html', c)

	else:

		c['cats'] = Yields.objects.all()

		return render(request, 'rm_report.html', c)




@login_required
def date_report(request):

	c={}
	c.update(csrf(request))

	if request.method == 'POST':
		date = request.POST.get('date', None)
		pdt = request.POST.get('pdt', None)

		try:
			item = Item.objects.get(id=pdt)
			pdt = Yields.objects.get(item=item)
		except Exception, e:
			pass


		x=[]
		n = []
		c['cou'] = OtherPrice.objects.filter(date=date , yields=pdt).order_by('country').values('country').distinct()

		j=1
		k=1
		for i in c['cou']:
			n.append(pdt)
			#n.append(i.size)
			#print i
			p = OtherPrice.objects.filter(date=date , yields=pdt, country__icontains=i['country'])
			for ii in p:
				#ii.price
				print ii.price
			#print p
			x.append( p )
			j = j+1
			

		#c['pri'] = OtherPrice.objects.filter(date=date , yields=pdt).order_by('country').values('price').distinct()

		c['pri'] = x

		#print x

		c['date'] = date
		c['cats'] = OtherPrice.objects.filter(date=date , yields=pdt)
		c['size'] = Size.objects.all()
		c['pdt'] = item

 		if date is not None: 			
 			return render(request, 'rm_price.html', c)

	else:
		c['cats'] = Yields.objects.all()


		return render(request, 'rm_report.html', c)


@login_required
def make_price(request):

	c = {}
	c.update(csrf(request))
	c['size'] = Size.objects.all()
	c['list'] = Yields.objects.all()
	c['hide'] = False

	return render(request, 'addIndianPrice.html', c)


@login_required
def show_report(request, date, country):

	c={}
	c.update(csrf(request))
	
	c['list'] = Yields.objects.all()

	return render(request, 'dateProductPrice.html', c)





@login_required
def get_piedate(request):
	c={}
	c.update(csrf(request))

	if request.method == "POST":		
		date1 = request.POST.get('date1','')
		date2 = request.POST.get('date2','')

		print date1
		print date2

		try:
			url = "http://getprojects.in/choice/api.ashx?action=getpie&date1="+str(date1)+"&date2="+str(date2)
			#url = "http://getprojects.in/choice/api.ashx?action=getpie&date1=2014-1-1&date2=2014-1-31"
			response = urllib2.build_opener().open(url).read()
		except Exception, e:

			messages.error(request, 'Poor Internet Connectivity!')
			return render(request, 'sel_rmdate.html', c)

		#response = [{"item" : "item1", "value" : 30}, {"item" : "item2", "value" : 70}]

		#return HttpResponse(response)
		c['resp'] = response

		return render(request, 'graph.html', c)

	return render(request, 'sel_rmdate.html', c)


MAX_DIGITS = 10
def _keyify(x):
	print x[0]
	x = x[0]
	
	xt = x.split(' ')
	x = xt[-1]

	try:
		xi = float(x)
	except ValueError:
		return 'S{0}'.format(x)
	else:
		return 'I{0:0{1}}'.format(xi, MAX_DIGITS)


@login_required
def get_rmdate(request):
	c={}
	c.update(csrf(request))

	if request.method == "POST":		
		date1 = request.POST.get('date1','')
		date2 = request.POST.get('date2','')
		
		date_list = fun(date1, date2)
		print date_list


		url = "http://getprojects.in/choice/api.ashx?action=getrm&date1="+str(date1)+"&date2="+str(date2) +"&cols="+str(len(date_list))
		print url

		data_dict = urllib2.build_opener().open(url).read()
		data_dict = ast.literal_eval(data_dict)

		data_dict = collections.OrderedDict(sorted(data_dict.items(), key=_keyify))


		try:
			url = "http://getprojects.in/choice/api.ashx?action=getrm&date1="+str(date1)+"&date2="+str(date2) +"&cols="+str(len(date_list))
			print url

			data_dict = urllib2.build_opener().open(url).read()
			data_dict = ast.literal_eval(data_dict)

			data_dict = collections.OrderedDict(sorted(data_dict.items(), key=_keyify))

		except Exception, e:

			messages.error(request, 'Poor Internet Connectivity!')
			return render(request, 'sel_rmdate.html', c)

		print data_dict


		#c['date_list'] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]
		#c['date_list'] = ["Jan", "Feb", "Mar", "Apr" ]
		#c['data_dict'] = {"i1" : [1,2,2,2], "i2" : [2,3,3,3], "i3" : [4,5,6,7]}

		c['date_list'] = date_list
		c['data_dict'] = data_dict

		return render(request, 'showRmReport.html', c)

	return render(request, 'sel_rmdate.html', c)



def fun(start, end):

	start = datetime.strptime(start, '%Y-%m-%d')
	end = datetime.strptime(end, '%Y-%m-%d')

	lst = []
	for result in perdelta(start, end, timedelta(days=25)):
		lst.append(result.strftime('%B'))

	lst = [min(j) for i, j in itertools.groupby(lst, key=lambda x: x[:7])]

	return lst



def perdelta(start, end, delta):
	curr = start
	while curr < end:
		yield curr
		curr += delta


#======================================== rm ====================================