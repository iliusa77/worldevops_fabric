from django.contrib import admin
from quote.models import *


admin.site.register(Customer)
admin.site.register(Packer)
admin.site.register(Terms)
admin.site.register(Item)
admin.site.register(Size)
admin.site.register(Pack)
admin.site.register(Brand)
admin.site.register(Destination)

admin.site.register(QuoteItem)
admin.site.register(QuoteInfo)

admin.site.register(LocationRelation)