#from django import forms
#from django.db import models
#from django.db.models import Q, F, Count
from django.contrib import admin
#from django.urls import reverse
from django.utils.html import format_html
#from django.utils.safestring import mark_safe
#from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect
from django.core.exceptions import ValidationError

from .setup import erp_admin, site_proxy, name_proxy

from ..models import OrderItemPrint, OrderItemCut, OrderItemWeld, OrderItemPack 
from ..models import OrderPrint, OrderCut, OrderWeld, OrderStuff, OrderPack
from .workstemplate import WorksTemplateInline, WorksOrderTemplate
from ..utils import ProductCategories

# Notes
# individual views per process, queryset filtered on process <'print', 'cut', 'weld', 'stuff', 'pack'>
#   methodology of generating these views may change
# **form is submitted automaticlly on pressing return** (which is good) 
#   also need keep scroll position (default is return to top)

# ------print------

class WorksPrintInline(WorksTemplateInline):
    model = OrderItemPrint
    tally = 'tally_print'
    total = 'print_total' #'print_tallytotal'
    complete = 'complete2'#'complete_print'
    readonly_fields = ['link_product','Bquantity','overprint', 'xnotes', total, 'remain', complete]
    fields = ('link_product','Bquantity','overprint','xnotes', tally, total,'remain', complete)
    process_lookup = 'product__type__print'
    verbose_name_plural = 'Print View'
    
   

@admin.register(OrderPrint, site=site_proxy)
class MPrintOrderAdmin(WorksOrderTemplate):
    inlines = [WorksPrintInline]
    product_category_name_totals = [mpc+'_remain_print' for mpc in ProductCategories]
    list_display = ['id','company','batch_info'] + product_category_name_totals
    readonly_fields = WorksOrderTemplate.readonly_fields+product_category_name_totals+['batch_info']
    #process_lookup = 'product__type__print'
    #listviewtitle = 'Print View: Items Remaining (of Total)'
    def changelist_view(self, request, extra_context=None):
        qq = format_html(
        '{} &nbsp&nbsp&nbsp <small><sup>{}<span style="color: #{}</sup>;">&nbsp<sub>{}</sub></small></span>',
        "Print View",  "remaining", '787878', "of total")
        extra_context = {'title': qq}
        return super().changelist_view(request, extra_context=extra_context)


#-----cut-------

class WorksCutInline(WorksTemplateInline):
    model =  OrderItemCut
    tally = 'tally_cut'
    total = 'cut_total'
    complete = 'complete2'
    readonly_fields = ['link_product','Bquantity','print_locations','xnotes', total, complete] 
    fields = ('link_product', 'Bquantity','print_locations', 'xnotes', tally, total, complete)
    process_lookup = 'product__type__cut'
    verbose_name_plural = 'Cut View'

@admin.register(OrderCut, site=site_proxy)
class WorksCutOrderAdmin(WorksOrderTemplate):
    inlines = [WorksCutInline]
    #process_lookup = 'product__type__cut'
    product_category_name_totals = [mpc+'_remain_cut' for mpc in ProductCategories]
    list_display = ['id','company'] + product_category_name_totals
    readonly_fields = WorksOrderTemplate.readonly_fields+product_category_name_totals
    def changelist_view(self, request, extra_context=None):
        qq = format_html(
        '{} &nbsp&nbsp&nbsp <small><sup>{}<span style="color: #{}</sup>;">&nbsp<sub>{}</sub></small></span>',
        "Cut View",  "remaining", '787878', "of total")
        extra_context = {'title': qq}
        return super().changelist_view(request, extra_context=extra_context)


#-----weld-------

class WorksWeldInline(WorksTemplateInline):
    model =  OrderItemWeld
    tally = 'tally_weld'
    total = 'weld_total'
    complete = 'complete2'
    readonly_fields = ['link_product','Bquantity','print_locations','xnotes', total, complete] 
    fields = ('link_product', 'Bquantity','print_locations', 'xnotes', tally, total, complete)
    process_lookup = 'product__type__weld'
    verbose_name_plural = 'Weld View'

@admin.register(OrderWeld, site=site_proxy)
class WorksCutOrderAdmin(WorksOrderTemplate):
    inlines = [WorksWeldInline]
    #process_lookup = 'product__type__cut'
    product_category_name_totals = [mpc+'_remain_weld' for mpc in ProductCategories]
    list_display = ['id','company'] + product_category_name_totals
    readonly_fields = WorksOrderTemplate.readonly_fields+product_category_name_totals
    def changelist_view(self, request, extra_context=None):
        qq = format_html(
        '{} &nbsp&nbsp&nbsp <small><sup>{}<span style="color: #{}</sup>;">&nbsp<sub>{}</sub></small></span>',
        "Weld View",  "remaining", '787878', "of total")
        extra_context = {'title': qq}
        return super().changelist_view(request, extra_context=extra_context)