from django import forms
from django.db import models
from django.db.models import Q, F, Count
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
#from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

from ..models import OrderItemOps, OrderOps 
from .workstemplate import  WorksOrderTemplate, admin2
from .inlines import WorksTemplateInline

from .setup import product_link, container_link
from .setup import erp_admin, site_proxy, name_proxy
from .setup import text_box

from ..utils import ss, setwidget, work_field_names 
from ..models import ProductCategories


# TODO
# class AdminForm(forms.ModelForm): # system works well (not used)
#     class Meta:
#         model = OrderItemOps
#         #import pdb; pdb.set_trace()   
#         fields = '__all__' 
#     widgets = { # works
#         'container': forms.Textarea(attrs={'cols': 30, 'rows': 2}),
#     }

class OpsTemplateInline(admin.TabularInline):
    model = OrderItemOps
    verbose_name_plural = 'Order Items - Operations Remaining to Complete' # inline title bar - correct
    extra = 0
    #form = AdminForm
    #description = True #?
    wft = [wfd + '_remain' for wfd in work_field_names]
    readonly_fields = ['product_link','type','quantity','progress', *wft] # changed from item_progress
    fields = ['product_link','type','quantity','progress', *wft]
    class Media:
        css = {'all': ('erp/hide_inline_title.css',)} 
        #js = ('erp/collapse_open.js',)
    def has_add_permission(self, request, obj=None):
         return False
    def has_delete_permission(self, request, obj=None):
        return False
    # def get_fieldsets(self, request, obj=None):    
    #     # example  
    #     #import pdb; pdb.set_trace()                                                               
    #     return super().get_fieldsets(request, obj)  
    def get_queryset(self, request): 
        qs = super().get_queryset(request)
        #if hasattr(self, 'process_lookup'): 
        #    qs = qs.filter(**{self.process_lookup : True})#.distinct().all()
        return qs #.filter(**{self.process_lookup : True})
    def product_link(self, obj): 
        #import pdb; pdb.set_trace() 
        if obj:
            return product_link(obj.product)


def order_complete_action(modeladmin, request, queryset):
     pass # TODO
order_complete_action.short_description = "Force Complete the select(ed) Orders"


# tr.totals {
#     background: aquamarine;
# }
@admin.register(OrderOps, site=site_proxy)
class OpsAdmin(WorksOrderTemplate):
    #def get_changelist_form(self, request, **kwargs):
    #    return xxxForm
    class Media:
        css = {'all': ('erp/label_width.css', )}
    inlines = [OpsTemplateInline]
    product_category_name_totals = [mpc+'_progress_all' for mpc in ProductCategories]

    list_display = ['id','company'] + product_category_name_totals +['OD','container_link']
    totals = [w +'_totals' for w in product_category_name_totals]
    totalsum_list = totals # crude hack implimented
    autocomplete_fields = ['container']
    #list_editable = ['container']
    #raw_id_fields =  ['container']
    #autocomplete_fields = ['container']
    readonly_fields = WorksOrderTemplate.readonly_fields+product_category_name_totals +['OD']+['LD_markup','CD_markup']
    fields = ['xmanufacture_notes','xdelivery_notes','container',('LD_markup','CD_markup')]
    actions = [order_complete_action]
    #listviewtitle = 'Operations View: Total Items (Progress)'
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'container':
            # disable any actions for that field
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False
        return formfield
    def changelist_view(self, request, extra_context=None):
        qq = format_html(
        '{} &nbsp&nbsp&nbsp <small><sup>{}<span style="color: #{}</sup>;">&nbsp<sub>{}</sub></small></span>',
        "Operations Order View",  "Total", '787878', "%Progress")
        qq = mark_safe(qq) # todo cannot get rid os markup showing
        extra_context = {'title': qq}#,'site_title':'tttt', 'site_header':'rrrrrr'}
        return super().changelist_view(request, extra_context=extra_context)
    def container_link(self, obj): 
        if obj:
            return container_link(obj.container)

 
