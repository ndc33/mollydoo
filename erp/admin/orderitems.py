from django import forms
from django.db import models
from django.db.models import Q, F, Count, Avg
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

#from simple_history.admin import SimpleHistoryAdmin

from ..models import OrderItem#, ProductType

from .setup import erp_admin, site_proxy, name_proxy
from .setup import text_box
from .setup import product_link, company_link, container_link 
from .workstemplate import TemplateFilter, admin2

from ..utils import ss, setwidget, work_field_names


class OrderItemview(OrderItem):
    class Meta:
        proxy = True
        verbose_name_plural = 'Order Items Overview'

class OrderItemOrderFilter(TemplateFilter): 
    title = 'Order'
    parameter_name = 'order'
    _lookup = 'order'

class OrderItemTypeFilter(TemplateFilter): 
    title = 'Type'
    parameter_name = 'type'
    _lookup = 'product__type__title'

class OrderItemBatchFilter(admin.SimpleListFilter): # todo (none's not working)
    title = 'container'
    parameter_name = 'container'
    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        types = qs.values_list('order__container__id','order__container__title')
        return list(types.order_by('order__container').distinct())
    def queryset(self, request, queryset):
        if self.value() is None:
            # todo return modified default filter set
            # return queryset.filter(state__complete=True)
            return queryset
        return queryset.filter(order__container__orders=self.value())


@admin.register(OrderItemview, site=site_proxy)
class OrderItemAdmin(admin2):
    # todo model-specific queryset with named annotations to prevent further queries? e.g.
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    wft = [wfd + '_remain' for wfd in work_field_names] # changed from '_total' and previous '_tallytotal'
    list_display = ('product_link','type','quantity',*wft,'opsorder_link','container_link')
    list_display_links = None
    totalsum_list = ['quantity'] + wft
    list_per_page = 50
    list_filter = (OrderItemTypeFilter, OrderItemOrderFilter, OrderItemBatchFilter)
    search_fields = ['order__company__name','order__id','order__container__title',
                    'product__title','product__category']
    producttitle = True
    suppress_form_controls = {
        'show_save_and_add_another': False,
        'show_delete': False,
        'title': 'Change this for a custom title.'
    }
    class Media:
        css = {'all': ('erp/label_width.css', )}
    class Meta:
        pass #verbose_name_plural = 'Test Order Items View'
    def changelist_view(self, request, extra_context=None):
        qq = format_html(
        '{} &nbsp&nbsp&nbsp <small><sup>{}<span style="color: #{}</sup>;">&nbsp<sub>{}</sub></small></span>',
        "Order Items View",  "Order quantities vs Processes Remaining", '787878', "")
        extra_context = {'title': qq}
        return super().changelist_view(request, extra_context=extra_context)
    def container_link(self, obj): 
        if obj:
            return container_link(obj.order.container)
    def opsorder_link(self, obj): 
        if obj:
            url = reverse(name_proxy +":erp_orderops_change", args=[obj.order.id]) 
            link = format_html('<a style="font-weight:bold" href="{}">{} </a>', url, obj.order)
            return mark_safe(link)
    opsorder_link.short_description = 'OpsOrder'
    def product_link(self, obj):
        if obj:
            return product_link(obj.product)
   
