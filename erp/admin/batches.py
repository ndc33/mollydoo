from django import forms
from django.db import models
from django.db.models import Q, F, Count
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
#from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

from ..models import Product, Order
from ..models import Container

from .setup import text_box
from .setup import erp_admin, site_proxy, name_proxy
from .setup import order_link
from .workstemplate import admin2

from ..utils import setwidget


class ContainerOrderInline(admin.TabularInline):
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
        if obj:
            return order_link(obj)


@admin.register(Container, site=site_proxy)
class ContainerAdmin(admin2):
    inlines = [ContainerOrderInline]
    formfield_overrides = text_box(3, 90)
    search_fields = ['titles'] #cannot get rid of html markup in search field
    list_display = ['title', 'dispatch_date', 'orders_list', 'notes'] 
    fields = ('title','dispatch_date','notes')
    
    suppress_form_controls = {
            'show_save_and_add_another': False,
            #'show_save': False, #(False interferes with ability to save on popups)
            #'show_delete': False
    }
    #formfield_overrides = text_box(3, 70)
    

