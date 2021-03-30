#from django import forms
from django.db import models
#from django.db.models import Q, F, Count
from django.contrib import admin
#from django.urls import reverse
#from django.utils.html import format_html
#from django.utils.safestring import mark_safe
#from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

#from import_export import resources
#from import_export.admin import ImportExportModelAdmin, ImportExportMixin

#from ..models import Address, Company, Contact, Product, Order
from ..models import ProductNote, OrderNote, OrderNoteItem  #, TestDynamic, create_model
#from .setup import product_link

from .setup import erp_admin, site_proxy, name_proxy, text_box
from .setup import company_link, product_link
from .workstemplate import admin2, TemplateFilter

"""
@admin.register(SpecNote, site=site_proxy)
class SpecNoteAdmin(admin2):
    remove_pk_controls = ['company','product','type']
    list_display = ['company','product','type', 'process', 'note']
"""

#"""
@admin.register(ProductNote, site=site_proxy)
class ProductNoteAdmin(admin2):
    class Media:
        css = {'all': ('erp/hide_inline_title.css', )}
    remove_pk_controls = ['product']
    list_display = ['company','product_link', 'process', 'note']
    list_display_links = None # details view disabled due to chained FK issue
    list_editable = ['note']
    formfield_overrides = text_box(1, 80)
    def company(self, obj):
        return obj.product.company.name
    pass
    def product_link(self, obj):
        return product_link(obj.product)

#"""

class OrderNoteCompanyFilter(TemplateFilter): 
    title = 'Company'
    parameter_name = 'name'
    _lookup = 'company__name'

class OrderNoteProcessFilter(TemplateFilter):
    title = 'Process'
    parameter_name = 'Process'
    _lookup = 'process'

@admin.register(OrderNote, site=site_proxy)
class OrderNoteAdmin(admin2):
    remove_pk_controls = ['product']
    list_display = ['company', 'process', 'note_html','highlight']
    #list_editable = ['note', 'highlight']
    fields = ['company', 'process', 'note','highlight']
    formfield_overrides = text_box(2, 80)
    list_filter = (OrderNoteCompanyFilter, OrderNoteProcessFilter)
    # def company(self, obj):
    #     return obj.product.company.name
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['company'] 
        return [] # object creation
    def company_link(self, obj): 
        return company_link(obj.company)

    

#@admin.register(OrderNoteItem, site=site_proxy)
class OrderNoteItemAdmin(admin2):
    remove_pk_controls = ['order']
    list_display = ['order', 'process', 'note', 'highlight']
    list_editable = ['note', 'highlight']
    fields = ['order', 'process', 'note', 'highlight']
    formfield_overrides = text_box(1, 80)
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['order'] 
        return [] # object creation
   
#@admin.register(type('TestDynamic2', (TestDynamic,), {'__module__': ''}), site=site_proxy)
#class TestDynamic(admin.ModelAdmin):
 #   pass

"""
vv = create_model(name='dynamic1', model=TestDynamic, ww = 'print')
@admin.register(vv, site=site_proxy)
class OrderNoteItemAdmin2(admin.ModelAdmin):
    fields = ['test','ww']
    readonly_fields = ['ww'] 
    pass

"""