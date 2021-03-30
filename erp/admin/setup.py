from django import forms
from django.db import models
#from django.db.models import Q, F, Count
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

#from simple_history.admin import SimpleHistoryAdmin
#from import_export import resources
#from import_export.admin import ImportExportModelAdmin, ImportExportMixin
#from django.apps import apps

from ..utils import ss, setwidget, get_related_field#, AccessMixin#, 

# prefetch notes
# https://hansonkd.medium.com/performance-problems-in-the-django-orm-1f62b3d04785
# https://stackoverflow.com/questions/51212021/django-prefetch-related-prefetch-nested
# https://stackoverflow.com/questions/27116770/prefetch-related-for-multiple-levels

def text_box(rows, cols):
    #https://stackoverflow.com/questions/18738486/control-the-size-textarea-widget-look-in-django-admin
    text_box = {  
            models.TextField: {'widget': forms.Textarea(
                            attrs={'rows': rows, 'cols': cols,})},#'style': 'height: 1em;'
        }
    return text_box

class ERP(admin.AdminSite):
    site_header = 'MollyDoo ERP'
    site_title = 'MollyDoo ERP'
    index_title = 'ERP'
    site_url = ''
    enable_nav_sidebar = False
    
erp_admin = ERP(name='erp')
site_proxy = erp_admin
name_proxy = 'erp' #'admin'

erp_admin.disable_action('delete_selected')
"""
def get_app_list(self, request):
    '''
    Return a sorted list of all the installed apps that have been
    registered in this site.
    '''
    ordering = {
        "Event heros": 1,
        "Event villains": 2,
        "Epics": 3,
        "Events": 4
    }
    app_dict = self._build_app_dict(request)
    # a.sort(key=lambda x: b.index(x[0]))
    # Sort the apps alphabetically.
    app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

    # Sort the models alphabetically within each app.
    for app in app_list:
        app['models'].sort(key=lambda x: ordering[x['name']])

        return app_list
"""

class TabularInline(admin.TabularInline): #AccessMixin, 
    def __getattr__(self, attr):
        if '__' in attr:
            return get_related_field(attr)
        return self.__getattribute__(attr)


def order_link(obj): 
    link = '-'
    if obj and hasattr(obj, 'id'):
        url = reverse(f'{name_proxy}:erp_order_change', args=[obj.id]) 
        link = format_html('<a style="font-weight:bold" href="{}">{} </a>', url, obj)
    return mark_safe(link)
order_link.short_description = 'Order'

def product_link(obj, style = "font-weight:bold"): 
    #style = "font-weight:bold;text-decoration:line-through"
    url = reverse(f'{name_proxy}:erp_product_change', args=[obj.id]) 
    link = format_html('<a style={} href="{}">{} </a>', style, url, obj)
    return mark_safe(link)
product_link.short_description = 'Product'      

def batch_link(obj): 
    link = '-'
    if obj and hasattr(obj, 'id'): # order list view gave error nontype has no attribute id
        # new
        url = reverse(f'{name_proxy}:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.id]) 
        #url = reverse(f'{name_proxy}:erp_batch_change', args=[obj.id]) 
        link = format_html('<a style="font-weight:bold" href="{}">{} </a>', url, obj)
    return link
batch_link.short_description = 'batch'


def company_link(obj): 
    link = '-'
    if obj and hasattr(obj, 'id'):
        url = reverse(f'{name_proxy}:erp_company_change', args=[obj.id]) 
        link = format_html('<a style="font-weight:bold" href="{}">{} </a>', url, obj)
    return mark_safe(link)
company_link.short_description = 'company'

def opsorder_link(obj): 
    link = '-'
    if obj and hasattr(obj, 'id'):
        url = reverse(name_proxy +":erp_orderall_change", args=[obj.order.id]) #_orderops_
        link = format_html('<a style="font-weight:bold" href="{}">{} </a>', url, obj.order)
    return mark_safe(link)
opsorder_link.short_description = 'OpsOrder'