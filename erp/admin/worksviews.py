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
from .workstemplate import WorksOrderTemplate
from .inlines import WorksTemplateInline
from ..models import ProductCategories


# ------print------

from ..models import SpecNote

class WorksPrintInlineNotes(WorksTemplateInline):
    model = SpecNote
    def get_queryset(self, request):
        # fundamental problem -> needs to have order pk to be included in an inline*****
        qs = super().get_queryset(request)
        # F example blog_name=F('blog__name')
        #qs2 = SpecNote.objects.filter()
        #     Q(company__id = self.company.id) | Q(company = None)
        #     ).filter(
        #      Q(type__id = None)
        #     ).all()
        #import pdb; pdb.set_trace()
        #return None#qs
        return qs#.filter('xxx')


class WorksPrintInline(WorksTemplateInline):
    model = OrderItemPrint
    verbose_name_plural = model.process + ' View'
       

@admin.register(OrderPrint, site=site_proxy)
class WorksPrintOrderAdmin(WorksOrderTemplate):
    inlines = [WorksPrintInline]
    class Media:
        css = {'all': ('erp/label_width.css', )}
    product_category_name_totals = [mpc+'_remain_print' for mpc in ProductCategories]
    # ,'order_process_specnotes'*************
    list_display = ['id','company'] + product_category_name_totals +['OD','container_link']
    totals_sum = [w+'_totals' for w in product_category_name_totals] # for the summary row
    totalsum_list = totals_sum
    readonly_fields = WorksOrderTemplate.readonly_fields+product_category_name_totals+['container']
    def changelist_view(self, request, extra_context=None):
        qq = format_html(
        '{} &nbsp&nbsp&nbsp <small><sup>{}<span style="color: #{}</sup>;">&nbsp<sub>{}</sub></small></span>',
        "Print View",  "remaining", '787878', "of total")
        extra_context = {'title': qq}
        return super().changelist_view(request, extra_context=extra_context)


#-----cut-------

class WorksCutInline(WorksTemplateInline):
    model =  OrderItemCut
    verbose_name_plural = model.process + ' View'

@admin.register(OrderCut, site=site_proxy)
class WorksCutOrderAdmin(WorksOrderTemplate):
    inlines = [WorksCutInline]
    class Media:
        css = {'all': ('erp/label_width.css', )}
    #process_lookup = 'product__type__cut'
    product_category_name_totals = [mpc+'_remain_cut' for mpc in ProductCategories]
    list_display = ['id','company'] + product_category_name_totals+['OD','container_link']
    totals_sum = [w+'_totals' for w in product_category_name_totals] # for the summary row
    totalsum_list = totals_sum
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
    verbose_name_plural = model.process + ' View'

@admin.register(OrderWeld, site=site_proxy)
class WorksCutOrderAdmin(WorksOrderTemplate):
    inlines = [WorksWeldInline]
    class Media:
        css = {'all': ('erp/label_width.css', )}
    #process_lookup = 'product__type__cut'
    product_category_name_totals = [mpc+'_remain_weld' for mpc in ProductCategories]
    list_display = ['id','company'] + product_category_name_totals + ['OD','container_link']
    totals_sum = [w+'_totals' for w in product_category_name_totals] # for the summary row
    totalsum_list = totals_sum
    readonly_fields = WorksOrderTemplate.readonly_fields+product_category_name_totals
    def changelist_view(self, request, extra_context=None):
        qq = format_html(
        '{} &nbsp&nbsp&nbsp <small><sup>{}<span style="color: #{}</sup>;">&nbsp<sub>{}</sub></small></span>',
        "Weld View",  "remaining", '787878', "of total")
        extra_context = {'title': qq}
        return super().changelist_view(request, extra_context=extra_context)