#------------manufacturing views-----------------

from django import forms
#from django.db import models
from django.db.models import Q, F, Count
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
#from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

from ..models import Order, OrderItem, ProductType
#from ..models import Product,

from .setup import erp_admin, site_proxy, name_proxy
from .setup import admin2, text_box

from ..utils import sumtally, ss, setwidget, work_field_names

# likely much cleaner/simpler was of obtaing the following functionilty

class OrderItemWorksView(OrderItem): # required for different __str__
    class Meta:
        proxy = True
    def __str__(self):
         return '%s of %s' % (self.quantity, self.product) 


class WorksTemplateInline(admin.TabularInline):
    model = OrderItemWorksView
    extra = 0
    description = True
    readonly_fields = ['xproduct','quantity','xnotes','total']# + self.rofields
    class Media:
        css = {'all': ('erp/hide_inline_title.css',)} #'erp/hide_inline_title.css',
        #js = ('erp/collapse_open.js',)
    def has_add_permission(self, request, obj=None):
         return False
    def has_delete_permission(self, request, obj=None):
        return False
    def get_fieldsets(self, request, obj=None):    
        # example                                                                 
        return super().get_fieldsets(request, obj)  
    def get_queryset(self, request): 
        qs = super().get_queryset(request)
        if hasattr(self, 'process_lookup'): 
            qs = qs.filter(**{self.process_lookup : True})#.distinct().all()
        return qs #.filter(**{self.process_lookup : True})
    def xproduct(self, obj): 
        #import ipdb; ipdb.set_trace() 
        if obj:
            batch_obj = obj.product
            url = reverse(name_proxy +":erp_product_change", args=[batch_obj.id]) 
            return format_html('<a style="font-weight:bold" href="{}">{} </a>', url, batch_obj)
    def total(self, obj):
        return sumtally(getattr(obj, self.tally))
    


class WorksOrderTemplate(admin2):
    id_obj = None
    save_on_top = True
    listviewtitle = 'custom title - list view' # place holder
    ordertitle = True
    suppress_form_controls = {
        'show_save_and_add_another': False,
        'show_delete': False,
        'show_save': False,
     #   'title': title
    }
    list_display = ['id','company','MD','batch_info']

    fields = ['xmanufacture_notes','xdelivery_notes'] # ('id','company', 'key_date') -> are in page title
    # ('company','id'),('MD','batch_info'),
    readonly_fields = ['batch_info','xmanufacture_notes','xdelivery_notes','created_at','modified','company','id','MD']
    class Media:
        pass #js = ('erp/q.js',)
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    def has_add_permission(self, request, obj=None):
        return False
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    #date_hierarchy = 'MD'
    def jobs_done(self, obj):
        return 
    def jobs_todo(self, obj):
        return 

