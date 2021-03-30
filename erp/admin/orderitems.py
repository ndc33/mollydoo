#from django import forms
from django.db import models
from django.db.models import Q, F, Count, Avg
from django.contrib import admin
#from django.urls import reverse
from django.utils.html import format_html
#from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

#from simple_history.admin import SimpleHistoryAdmin

from ..models import OrderItem  #WorksOrderItemAll   #OrderItem#, ProductType

from .setup import erp_admin, site_proxy, name_proxy
from .setup import text_box
from .setup import product_link, company_link, batch_link, opsorder_link
from .workstemplate import TemplateFilter, admin2

from ..utils import ss, setwidget, work_field_names

class OrderItemOrderFilter(TemplateFilter): 
    title = 'Order'
    parameter_name = 'order'
    _lookup = 'order'

class OrderItemTypeFilter(TemplateFilter): 
    title = 'Type'
    parameter_name = 'type'
    _lookup = 'product__type__title'

class OrderItemBatchFilter(admin.SimpleListFilter): # todo (none's not working)
    title = 'batch'
    parameter_name = 'batch'
    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        types = qs.values_list('order__batch__id','order__batch__title')
        return list(types.order_by('order__batch').distinct())
    def queryset(self, request, queryset):
        if self.value() is None:
            # todo return modified default filter set
            # return queryset.filter(state__complete=True)
            return queryset
        return queryset.filter(order__batch__orders=self.value())



@admin.register(OrderItem, site=site_proxy) # WorksOrderItemAll
class OrderItemAdmin(admin2):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        html = format_html('<span style="color: #{};">{}</span>', '008000', 'tttgreen')
        qs = qs.annotate(ttt=models.Value(html, output_field=models.TextField())) # testing
        return qs
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    wft = [f'__{wfd}_remain2__({wfd})' for wfd in work_field_names] # _2 query
    ptype = '__product__type__title__(type)' # 'type'
    list_display = ['opsorder_link','product_link', ptype,'quantity',*wft,'batch_link']
    #,'__ggg','__ttt','__myfunc2__(88,test)']#,'__ppp__html')
    list_display_links = None
    totalsum_list = ['quantity'] + wft
    list_per_page = 50
    list_filter = (OrderItemTypeFilter, OrderItemOrderFilter, OrderItemBatchFilter)
    search_fields = ['order__company__name','order__id','order__batch__title',
                    'product__title','product__type__title']
    producttitle = True
    # suppress_form_controls = {
    #     'show_save_and_add_another': False,
    #     'show_delete': False,
    #     'title': 'Change this for a custom title.'
    # }
    class Media:
        css = {'all': ('erp/label_width.css', )}
    class Meta:
        verbose_name_plural = 'Works Order Items All'
    def changelist_view(self, request, extra_context=None):
        qq = format_html(
        '{} &nbsp&nbsp&nbsp <small><sup>{}<span style="color: #{}</sup>;">&nbsp<sub>{}</sub></small></span>',
        "Order Items View",  "Order quantities vs Processes Remaining", '787878', "")
        extra_context = {'title': qq}
        return super().changelist_view(request, extra_context=extra_context)
    def batch_link(self, obj):
        return batch_link(obj.order.batch)
    batch_link.admin_order_field = 'order__batch__dispatch_date'
    def opsorder_link(self, obj):
        return opsorder_link(obj)
    opsorder_link.admin_order_field = 'order'
    #ppppp
    def product_link(self, obj):
        return product_link(obj.product)
    def order_notes(self):
        pass #???
   
