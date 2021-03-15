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

#from simple_history.admin import SimpleHistoryAdmin

from ..models import Product, ProductType, ProductDisplayCategory

from .setup import erp_admin, site_proxy, name_proxy
from .setup import text_box
from .workstemplate import TemplateFilter, admin2

from ..utils import ss, setwidget, work_field_names

@admin.register(ProductDisplayCategory, site=site_proxy)
class ProductDisplayCategoryAdmin(admin2):
    list_display = ['title','type_count']

@admin.register(ProductType, site=site_proxy)
class ProductTypeAdmin(admin2):
    list_display = ['title','category','product_count'] + work_field_names # ('__all_',) for info
    readonly_fields = ('id',)
    search_fields = ['title','category']
    remove_pk_controls = ['category']
    class Meta:
        pass
        # widgets = {
        #     'id_code': forms.TextInput(attrs={'class': 'label_width.css'}),
        # }
    class Media:
       css = {'all': ('erp/label_width.css', )}



class ProductTypeFilter(TemplateFilter): 
    title = 'Product Type'
    parameter_name = 'type'
    _lookup = 'type__title'

class ProductCompanyFilter(TemplateFilter):
    title = 'Company'
    parameter_name = 'company'
    _lookup = 'company__name'


@admin.register(Product, site=site_proxy)
class ProductAdmin(admin2):
    list_display = ('title','type','company','price','active') 
    autocomplete_fields = ['company','type']
    save_as = True
    list_filter = (ProductTypeFilter, ProductCompanyFilter)
    search_fields = ['title', 'type__category','type__title', 'company__name']#'type__code',
    formfield_overrides = text_box(3, 70)
    remove_pk_controls = ['company', 'type']
 
