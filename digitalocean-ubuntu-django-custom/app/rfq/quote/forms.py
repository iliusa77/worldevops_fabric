from django import forms
from .models import *

import html5.forms.widgets as html5_widgets



class QuoteEntryForm(forms.ModelForm):

    requester = forms.ModelChoiceField(label="Name Of Requester",queryset=User.objects.all())
    packer = forms.ModelChoiceField(label="Name Of Packer",queryset=Packer.objects.all())
    location = forms.ChoiceField(label="Select Location", choices=QuoteInfo.LOCATIONS)
    #delivery_date = forms.DateField(widget = html5_widgets.DateInput, label='Delivery Date')
    #valid_date = forms.DateField(widget = html5_widgets.DateInput, label='Valid Date', required=False)
    item_type = forms.ChoiceField(widget=forms.RadioSelect, choices=QuoteInfo.TYPE_CHOICES, label='')
   
    class Meta:
        model = QuoteInfo
        exclude = ['items', 'valid_date', 'container_number', 'po', 'status', 'alert', 'approver_remarks','requester_remarks', 'final_approver_remarks']
        widgets = {
            'specifications': forms.Textarea(attrs={'style' : 'height:100px;'})
        }

    def __init__(self, *args, **kwargs):
        super(QuoteEntryForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs = {'class':'form-control'}        



class QuoteItemForm(forms.ModelForm):

    #quantity = forms.DecimalField(label='Qty(LBS)')

    class Meta:
        model = QuoteItem
        exclude = ['indication_selling_price', 'selling_price', \
        	'quoted_price','final_price', 'counter_offer', \
        	'remarker_remarks', 'gross_profit', 'currency']


    def __init__(self, *args, **kwargs):
        super(QuoteItemForm, self).__init__(*args, **kwargs)

        for key in self.fields.keys():
            self.fields[key].widget.attrs = {'class':'form-control'}
    
