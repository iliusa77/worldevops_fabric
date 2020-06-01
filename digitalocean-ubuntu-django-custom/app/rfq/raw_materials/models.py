from django.db import models
from quote.models import Size, Item
# Create your models here.

class Yields(models.Model):
    
    item  = models.ForeignKey(Item)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __unicode__(self):
        return '{0}'.format(self.item)



class OtherPrice(models.Model):
    """model for Other RM Price"""

    yields = models.ForeignKey(Yields)
    size = models.ForeignKey(Size)
    #cpto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #rpto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #ezpl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #cpnd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #rpnd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date = models.DateField()
    country = models.CharField(max_length=50)

    def __unicode__(self):
        return '{0}'.format(self.yields)


class Rates(models.Model):
    """docstring for Rates"""

    rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expense = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __unicode__(self):
        return '{0}'.format(self.rate)


class RmPrice(models.Model):
    yields = models.ForeignKey(Yields)
    size = models.ForeignKey(Size)

    india = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    indonesia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    thailand = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vietnam = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    india_other = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    date = models.DateField()


    def __unicode__(self):
        return '{0}'.format(self.yields)