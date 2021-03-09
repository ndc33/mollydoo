#from django import forms
#from django.db import models
from django.db.models import Q, F, Count
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
#from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

from .setup import erp_admin, site_proxy, name_proxy

from ..models import OrderItemOps, OrderOps  # OrderItem,  Order,
from .workstemplate import WorksTemplateInline, WorksOrderTemplate, link_product#, OrderItemWorksView

from .setup import erp_admin, site_proxy, name_proxy
from .setup import admin2, text_box

from ..utils import ss, setwidget, work_field_names, ProductCategories


# TODO
# list view should show a list of orders with ['company','orderid', 'CM', 'SPLASH', 'ARM', 'Mattress'] etc 
#   with the total number outstanding vs total (display as fraction with top more emphasised?) should also have a custom 
#   action to mark as complete. 
# The change-view page should show a list of order items, (like works-change-view) with ALL processes with the same 
#   remaining/total and a checkbox per row to save-as-complete.
# issue regards having columns generated per product catogary which is user defined db data. Will likely have to generating 
#   custom form with dynamic fields OR simpley have the standard product categories + 'other'
'''
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum

#http://azamatpsw.blogspot.com/2012/01/django-adding-row-to-admin-list-with.html
# better ideas here https://stackoverflow.com/questions/8541956/django-admin-add-extra-row-with-totals
#from myapp.models import MyModelName
MyModelName = Order

class TotalAveragesChangeList(ChangeList):
    #provide the list of fields that we need to calculate averages and totals
    fields_to_total = ['tCM']
 
    def get_total_values(self, queryset):
        """
        Get the totals
        """
        #basically the total parameter is an empty instance of the given model
        total =  MyModelName()
        total.custom_alias_name = "Totals" #the label for the totals row
        for field in self.fields_to_total:
            setattr(total, field, queryset.aggregate(Sum(field)).items()[0][1])
        return total

    def get_results(self, request):
        """
        The model admin gets queryset results from this method
        and then displays it in the template
        """
        super().get_results(request)
        #first get the totals from the current changelist
        total = self.get_total_values(self.queryset) #(self.query_set
        #then get the averages
        #average = self.get_average_values(self.query_set)
        #small hack. in order to get the objects loaded we need to call for 
        #queryset results once so simple len function does it
        len(self.result_list)
        #and finally we add our custom rows to the resulting changelist
        self.result_list._result_cache.append(total)
        #self.result_list._result_cache.append(average)

'''
#-------------


class OpsTemplateInline(admin.TabularInline):
    model = OrderItemOps
    verbose_name_plural = 'Order Items - Operations Remaining to Complete' # inline title bar - correct
    extra = 0
    #description = True #?
    #wft = [wfd + '_remaining' for wfd in work_field_names]
    wft = [wfd + '_remain' for wfd in work_field_names]
    ##product_category_name_totals = [mpc+'_remain_cut' for mpc in ProductCategories]
    #wft = 
    readonly_fields = ['link_product','quantity', 'progress', *wft] # changed from item_progress
    fields = ['link_product','quantity', 'progress', *wft]
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
        #if hasattr(self, 'process_lookup'): 
        #    qs = qs.filter(**{self.process_lookup : True})#.distinct().all()
        return qs #.filter(**{self.process_lookup : True})
    def link_product(self, obj): 
        if obj:
            return link_product(obj.product)


def order_complete_action(modeladmin, request, queryset):
     pass # TODO
order_complete_action.short_description = "Force Complete the select(ed) Orders"


@admin.register(OrderOps, site=site_proxy)
class OpsAdmin(WorksOrderTemplate):
    inlines = [OpsTemplateInline]
    product_category_name_totals = [mpc+'_progress_all' for mpc in ProductCategories]
    list_display = ['id','company'] + product_category_name_totals #+['container']
    #list_editable = ('container',)
    readonly_fields = WorksOrderTemplate.readonly_fields+product_category_name_totals
    actions = [order_complete_action]
    #listviewtitle = 'Operations View: Total Items (Progress)'
    def changelist_view(self, request, extra_context=None):
        qq = format_html(
        '{} &nbsp&nbsp&nbsp <small><sup>{}<span style="color: #{}</sup>;">&nbsp<sub>{}</sub></small></span>',
        "Operations View",  "Total", '787878', "%Progress")
        extra_context = {'title': qq}
        return super().changelist_view(request, extra_context=extra_context)
    # TODO add annotations
    # def get_queryset(self, request): 
    #     qs = super().get_queryset(request)
    #     qs = qs.annotate()
    # def get_formset(self, request, obj=None, **kwargs):
    #     formset = super().get_formset(request, obj, **kwargs)
    #     form = formset.form
    #     if w:= form.base_fields.get('container'):
    #         w.widget.can_change_related = False
    #         w.widget.can_delete_related = False
    #         w.widget.can_add_related = True
    #         #setwidget(w.widget)
    #     return formset

 
