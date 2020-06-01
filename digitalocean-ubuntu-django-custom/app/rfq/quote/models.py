from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return '{0}'.format(self.name)

class Packer(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return '{0}'.format(self.name)

class Terms(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return '{0}'.format(self.title)

class Item(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return '{0}'.format(self.name)

class Size(models.Model):
    size = models.CharField(max_length=200)

    def __unicode__(self):
        return '{0}'.format(self.size)

class Pack(models.Model):
    pack = models.CharField(max_length=200)

    def __unicode__(self):
        return '{0}'.format(self.pack)

class Brand(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return '{0}'.format(self.name)


class Destination(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return '{0}'.format(self.name)




class QuoteItem(models.Model):
    '''
    Model to store the RFQ item data
    '''

    item = models.ForeignKey(Item)
    size = models.ForeignKey(Size)
    pack = models.ForeignKey(Pack)
    brand = models.ForeignKey(Brand)
    cases = models.IntegerField()
    quantity_in_lbs = models.DecimalField(max_digits=15, decimal_places=2)
    indication_selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=20, null=True, blank=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    counter_offer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gross_profit = models.FloatField(null=True, blank=True)    

    
    def __unicode__(self):
        return '{0} - {1}'.format(self.id, self.item)



class LocationRelation(models.Model):
    """docstring for LocationRelation"""

    LOCATIONS = (
        ('Can', 'Canada'),
        ('US', 'US'),
    )

    location = models.CharField(max_length=30, choices=LOCATIONS)
    packer = models.ForeignKey(Packer, null=True, blank=True)
    customer = models.ForeignKey(Customer, null=True, blank=True)
    destination = models.ForeignKey(Destination, null=True, blank=True)

    def __unicode__(self):
        return '{0} - {1} - {2} - {3}'.format(self.location, self.packer, self.customer, self.destination)



class QuoteInfo(models.Model):
    '''
    Quote request general info
    '''

    STATUS = (
        ('rfq_generated', 'RFQ Generated'),
        ('response_received', 'Response Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('counter_price_added', 'Counter Price Added'),
        ('generate_po', 'Generate PO'),
        ('po_issued', 'PO Issued'),
        ('shipped', 'Shipped'),
        ('cancelled_by_user', 'Cancelled By User'),
        ('counter_response_received', 'Counter Received'),
        ('counter_offer_accepted', 'Counter Offer Accepted'),
    )

    OFFICE_LOCATIONS = (
        ('Choice NJ', 'Choice NJ'),
        ('Choice Canada', 'Choice Canada'),
        ('Choice LA', 'Choice LA'),
        ('Choice TAMPA', 'Choice Tampa'),
    )

    TYPE_CHOICES = (
        ('presold', 'PRE SOLD'),
        ('not_sold', 'NOT SOLD'),
    )

    LOCATIONS = (
        ('Can', 'Canada'),
        ('US', 'US'),
    )

    TERMS = (
        ("LC", "LC"),
        ("DA", "DA"),
        ("DP", "DP"),
        ("Wire Transfer", "Wire Transfer"),
        ("AFTER FDA PASSAGE", "AFTER FDA PASSAGE"),
    )

    date = models.DateField()
    office_location = models.CharField(max_length=30, choices=OFFICE_LOCATIONS)
    requester = models.ForeignKey(User)
    location = models.CharField(max_length=30, choices=LOCATIONS)
    packer = models.ForeignKey(Packer,null=True, blank=True)
    terms_of_purchase = models.CharField(max_length=50, choices=TERMS, null=True, blank=True)
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES, null=True, blank=True)
    customer = models.ForeignKey(Customer, null=True, blank=True)
    terms_of_sale = models.CharField(max_length=50, null=True, blank=True)
    destination = models.ForeignKey(Destination, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    valid_date = models.DateField(null=True, blank=True)

    items = models.ManyToManyField(QuoteItem)

    po = models.CharField(max_length=100, null=True, blank=True)
    container_number = models.CharField(max_length=50, null=True, blank=True)

    specifications = models.CharField(max_length=1000, null=True, blank=True)
    port_of_delivery = models.CharField(max_length=100, null=True, blank=True)
    type_of_delivery = models.CharField(max_length=100, null=True, blank=True)

    alert = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=STATUS)

    approver_remarks = models.TextField(null=True, blank=True)
    requester_remarks = models.TextField(null=True, blank=True)
    final_approver_remarks = models.TextField(null=True, blank=True)


    def __unicode__(self):
        return 'RFQ/{0}/{1} - {2} - {3} - {4}'.format(self.location, self.id, self.requester, self.status, str(self.date))

    def as_dict(self):
        return {
            "id": self.id,
            "item" : self.items,
            "price": self.items.price,
        }


class Alert(models.Model):
    to_user     = models.OneToOneField(User, null=True, blank=True)
    from_user   = models.OneToOneField(User, null=True, blank=True, related_name='from_user')
    itm         = models.ForeignKey(QuoteItem, null=True, blank=True)
    alert       = models.BooleanField(default=False)

    def __unicode__(self):
        return '{0}'.format(self.to_user)



class Remarks(models.Model):

    rfq         = models.ForeignKey(QuoteInfo, null=True, blank=True)
    from_user   = models.ForeignKey(User, null=True, blank=True)
    remark      = models.CharField(max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return '{0} - {1}'.format(self.rfq, self.from_user)


