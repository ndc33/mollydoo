#from django import forms
#from django.db import models
from django.db.models import Q, F, Count
from django.contrib import admin
#from django.urls import reverse
#from django.utils.html import format_html
#from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

from ..models import Order #Product
from ..models import Batch

from .setup import text_box
from .setup import erp_admin, site_proxy, name_proxy
from .setup import order_link
from .workstemplate import admin2

from ..utils import setwidget


class BatchOrderInline(admin.TabularInline):
    model = Order
    extra = 0
    #show_change_link = True
    #list_display = ('title', 'type', 'active')
    fields = ('order_link', 'company','OD','LD_markup','CD_markup')#,'container') # will not show container key
    readonly_fields=('order_link','id','company','OD','LD_markup','CD_markup')
    class Media:
        css = {'all': ('erp/hide_inline_title.css', )}
    def has_add_permission(self, request, obj=None):
         return False
    #def has_delete_permission(self, request, obj=None):
    #    return False
    def order_link(self, obj):
        return order_link(obj)


@admin.register(Batch, site=site_proxy)
class BatchAdmin(admin2):
    #inlines = [BatchOrderInline]
    formfield_overrides = text_box(3, 90)
    search_fields = ['title'] #cannot get rid of html markup in search field
    list_display = ['title', 'dispatch_date', 'orders_list', 'notes'] 
    fields = ('title','dispatch_date','notes')
    def get_inlines(self, request, obj=None):
        if not obj: 
            # Return no inlines when obj is being created. For info, see also add_view() and change_view()   
            return []
        return [BatchOrderInline]
    def has_delete_permission(self, request, obj=None):
        if 'popup' in request.get_full_path():
            pass#import pdb; pdb.set_trace()
        return False

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        vv =  super().render_change_form(request, context, add, change, form_url, obj)
        if 'popup' in request.get_full_path():
            context.update({'show_save': True})
            #import pdb; pdb.set_trace()
        return vv
    

