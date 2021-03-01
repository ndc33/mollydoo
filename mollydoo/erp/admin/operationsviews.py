#from django import forms
#from django.db import models
from django.db.models import Q, F, Count
from django.contrib import admin
#from django.urls import reverse
#from django.utils.html import format_html
#from django.utils.safestring import mark_safe
#from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

from .setup import erp_admin, site_proxy, name_proxy

from ..models import Order, OrderItem 
from .workstemplate import WorksTemplateInline, WorksOrderTemplate

from .setup import erp_admin, site_proxy, name_proxy
from .setup import admin2, text_box

from ..utils import ss, setwidget, work_field_names


# TODO
# list view should show a list of orders with ['company','orderid', 'CM', 'SPLASH', 'ARM', 'Mattress'] etc 
#   with the total number outstanding vs total (display as fraction with top more emphasised?) should also have a custom 
#   action to mark as complete. 
# The change-view page should show a list of order items, (like works-change-view) with ALL processes with the same 
#   remaining/total and a checkbox per row to save-as-complete.
# issue regards having columns generated per product catogary which is user defined db data. Will likely have to generating 
#   custom form with dynamic fields OR simpley have the standard product categories + 'other'

class OpsView(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Operations View'
    # def CM(self):
    #     return self.item.product.quantity
    

@admin.register(OpsView, site=site_proxy)
class OpsAdmin(WorksOrderTemplate):
    pass #inlines = [OpsInline]
    #process_lookup = 'product__type__print'
    list_display = ['id','company','CM']#,'Splash','M']
    
    readonly_fields = WorksOrderTemplate.readonly_fields+['CM']
    def CM(self, obj): 
        #playing with queries - note importance of reverse transversal over 'item'
        thisorderitems = OrderItem.objects.filter(id=obj.id)
        cats = Order.objects.annotate(count=Count('item__product__type__code'))
        #import ipdb; ipdb.set_trace() 
        return 1

