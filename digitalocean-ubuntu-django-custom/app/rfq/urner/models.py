from django.db import models


# Create your models here.

class Product(models.Model):

	name  = models.CharField(max_length=700)

	def __unicode__(self):
		return '{0}'.format(self.name)


class ProductDetails(models.Model):
	"""Store details ProductDetails"""

	product = models.ForeignKey(Product)
	price = models.CharField(max_length=100)
	date  = models.DateField()

	def __unicode__(self):
		return '{0}'.format(self.name)