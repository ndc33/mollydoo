
from django import forms
#from django.db import models
#from django.db.models import Q, F, Count
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
#from django.utils.safestring import mark_safe
#from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect


from .setup import erp_admin, site_proxy, name_proxy
from .setup import text_box
from .setup import product_link
from .workstemplate import admin2

from ..utils import  ss, setwidget


class WorksTemplateInline(admin.TabularInline):
    #model = #-> defined on inheritance
    extra = 0
    description = True #?
    class Media:
        css = {'all': ('erp/hide_inline_title.css',)}
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
        #if hasattr(self, 'process_lookup'): used to be defined in worksviews
        #    qs = qs.filter(**{self.process_lookup : True})
        qs = qs.filter(**{'product__type__'+self.model.process : True})
        return qs
    def product_link(self, obj): 
        if obj:
            style =  "text-decoration:line-through" if obj.complete2 else "font-weight:bold"
            return product_link(obj.product, style)
    readonly_fields = ['product_link','type','quantity_html','overprints', 'xnotes', 'remain', 'total_html','print_locations']
    def get_fields(self, request, obj=None):
        process = self.model.process 
        default = ['product_link','type','quantity_html','xnotes', 'tally_'+ process, 'total_html','remain']
        if process in ['cut', 'weld']: 
            default.insert(3, 'print_locations')
        if process == 'print':
            default.insert(3, 'overprints')
        return default

