from django import forms
from django.db import models
#from django.db.models import Q, F, Count
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
#from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportMixin

from ..models import Address, Company, Contact, Product, Order#, SpecNote
from .workstemplate import link_product

from .setup import erp_admin, site_proxy, name_proxy
from .setup import admin2, text_box

#from ..utils import 

# TODO
# the present assosiation of addresses with companies is a mess, exploration of having multiple delivery addresses for
#   the same invoice entity -> we serve trade who drop ship to trade. Ongoing

class ContactInline(admin.TabularInline):
#class ContactInline(admin.StackedInline):
    model = Contact
    extra = 0
    class Media:
        css = {'all': ('erp/hide_inline_title.css', )}
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
         return False


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
         return False
    
class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    fields = ['link_id','company','OD','LD_markup','CD_markup','batch_info','status'] 
    readonly_fields = ['link_id','company','OD','LD_markup','CD_markup', 'batch_info','status'] 
    class Media:
        css = {'all': ('erp/hide_inline_title.css', )}
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
         return False
    def link_id(self, obj): 
        if obj:
            url = reverse(name_proxy +":erp_order_change", args=[obj.id]) 
        return format_html('<a style="font-weight:bold" href="{}">{} </a>', url, obj)
    link_id.short_description = '<Order>' 


class AddressAdmin(ImportExportMixin, admin2):
    #resource_class = AddressResource # keep
    list_display = ('name', 'company', 'type')
    #history_list_display = ['changed_fields'] #keep
    remove_pk_controls = ['company']
    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            #return delta.changed_fields # origional stackoverflow
            return [change.field for change in delta.changes]
        return None
erp_admin.register(Address, AddressAdmin)#, site=site_proxy)  # standard method -> @property will be fully fixed in Django 3.2


@admin.register(Contact, site=site_proxy)
class ContactAdmin(admin2):
    list_display = ('name', 'company', 'role')
    remove_pk_controls = ['company']
    

# @admin.register(SpecNote, site=site_proxy)
# class ContactAdmin(admin2):
#     remove_pk_controls = ['company', 'product']


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('link_product', 'type', 'price', 'notes', 'active') # 'title',
    readonly_fields = ['link_product']
    def has_delete_permission(self, request, obj=None):
         return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
    def link_product(self, obj): 
        if obj:
            return link_product(obj)
    # keep following for info
    # classes = ['collapse']
    # def response_add(self, request, obj, post_url_continue=None):
    #     return redirect('/erp/erp/product/add/')
    # def response_change(self, request, obj):
    #     return redirect('/erp/erp/product/add/')
   


@admin.register(Company, site=site_proxy)
class CompanyAdmin(admin2):
    save_on_top = True
    formfield_overrides = text_box(3, 70)
    class Media:
        css = {'all': ('erp/label_width.css', )}
    suppress_form_controls = {
        'show_save_and_add_another': False,
        'show_delete': False,
        'title': 'Change this for a custom title.'
    }
    listviewtitle = 'custom title - list view todo'
    list_display = ('name', 'type', 'status')
    def get_fields(self, request, obj=None):
        return (
            ('name',  'shortname', 'codename'), ('type',  'status'), ('VAT_Number', 'tax_status'), 
            'office_notes', 'order_notes', 'manufacture_notes', 'delivery_notes',
            ('created_at', 'modified')
            )
    def get_readonly_fields(self, request, obj=None):
        default = ['created_at', 'modified']
        if obj:
            return default+['name']
        return default
    def get_inlines(self, request, obj=None):
        if not obj: 
            # Return no inlines when obj is being created. For info, see also add_view() and change_view()   
            return []
        return [ContactInline, AddressInline, ProductInline, OrderInline]
   
# ----------- ignore--------------------

# #@admin.register(Address, site=site_proxy)
# class AddressHistoryAdmin(SimpleHistoryAdmin): 
#     # https://django-simple-history.readthedocs.io/en/2.12.0/history_diffing.html
#     list_display = ["id", "name"]#, 'changed_fields']
#     #history_list_display = ["status"]
#     #search_fields = ['name', 'user__username']
#     #history_list_display = ['changed_fields']

#     def changed_fields(self, obj):
#         if obj.prev_record:
#             delta = obj.diff_against(obj.prev_record)
#             #return delta.changed_fields # origional stackoverflow
#             return delta.changes.field
#         return None
# # type, name, address, postcode

# admin.site.register(Address, AddressHistoryAdmin, site=site_proxy)