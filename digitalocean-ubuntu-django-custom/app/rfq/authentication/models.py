from django.db import models
from django.contrib.auth.models import User



class New(models.Model):

	title = models.TextField(null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	display = models.BooleanField(default=True, blank=True)
	pub_date = models.DateField(auto_now=True)


	def __unicode__():
		return self.title
	
