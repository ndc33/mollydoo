#from django import forms
from django.db import models
#from django.db.models import Q, F, Count
from django.contrib import admin
#from django.urls import reverse
#from django.utils.html import format_html
#from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

#from simple_history.admin import SimpleHistoryAdmin

from ..models import Product, ProductType, ProductDisplayCategory
from ..models import ProductRange, ProductNote
from ..models import OrderItem

from .setup import erp_admin, site_proxy, name_proxy
from .setup import text_box
from .workstemplate import TemplateFilter, admin2

from ..utils import ss, setwidget, work_field_names

from .orders import OrderItemInline


#@admin.register(ProductRange, site=site_proxy)
class ProductRangeAdmin(admin2):
    pass

@admin.register(ProductDisplayCategory, site=site_proxy)
class ProductDisplayCategoryAdmin(admin2):

    list_display = ['title','type_count','typecounttest','__type__count__('',Type Count)']#, '__hhh','__jj3']
    #@property
    def typecounttest(self, obj):
        return obj.type.count()
    def totals_sum(self, obj):
        return ['type_count', 'typecounttest','__type__count__('',Type Count)']  #getattr(self.model, 'typecounttest', ()) #totals_summary_row
    #for totals self has typecounttest function access and needs to be fed (obj) an item of filtered_query_set
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        #html = format_html('<span style="color: #{};">{}</span>', '008000', '6')
        qs = qs.annotate(hhh=models.Value(6, output_field=models.IntegerField())) # testing
        return qs

@admin.register(ProductType, site=site_proxy)
class ProductTypeAdmin(admin2):
    list_display = ['title','category','product_count'] + work_field_names # ('__all_',) for info
    readonly_fields = ('id',)
    search_fields = ['title','category__title']
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


class ProductNoteInline(admin.TabularInline):
    model = ProductNote
    class Media:
        css = {'all': ('erp/hide_inline_title.css',)}
    extra = 0
    formfield_overrides = text_box(1, 90)
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        #import pdb; pdb.set_trace()
        if db_field.name == "process" and kwargs.get('object_id'):
            obj_id = request.resolver_match.kwargs['object_id'] 
            wfd = Product.objects.get(id=obj_id).type.workfields_defined + ['all']
            choices = zip(wfd,wfd)
            kwargs['choices'] = choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)



class OrderItemInline(admin.TabularInline):
#class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    formfield_overrides = text_box(1, 30)
    notes = 'all_notes' #'qnotes'# not sure this is required or relevant
    fields = ('order','orderdate','xprice','quantity', notes)
    readonly_fields =  ('order','orderdate', notes,'xprice','quantity')
    verbose_name_plural = 'Included in the following Orders'
    class Media:
        css = {'all': ('erp/hide_inline_title.css', )}
    myobject_id = None
    def order(self, obj):
        return obj.order
    def orderdate(self, obj):
        return obj.order.OD
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
         return False


@admin.register(Product, site=site_proxy)
class ProductAdmin(admin2):
    list_display = ['title','type','company','price','sales_count','active']
    autocomplete_fields = ['company','type']
    #save_as = True
    list_filter = (ProductTypeFilter, ProductCompanyFilter)
    search_fields = ['title', 'type__category__title','type__title', 'company__name']#'type__code',
    formfield_overrides = text_box(3, 70)
    remove_pk_controls = ['company', 'type']
    def get_inlines(self, request, obj=None):
        if obj: 
            return [ProductNoteInline,OrderItemInline]
        # no inlines on obj creation. For info, see also add_view() and change_view()   
        return  []#[ProductNoteInline]
   
 
