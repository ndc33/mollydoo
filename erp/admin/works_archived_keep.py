"""
#------------manufacturing views-----------------

from django import forms
#from django.db import models
#from django.db.models import Q, F
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
#from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

from ..models import Order, OrderItem, ProductType#, OrderItem_adminview#, PrintOrder
#from ..models import Product,

from .setup import erp_admin, site_proxy, name_proxy
from .setup import admin2, text_box

from ..utils import sumtally, ss, setwidget, work_field_names


class OrderItemWorksView(OrderItem): # required for different __str__
    class Meta:
        proxy = True
    def __str__(self):
         return '%s of %s' % (self.quantity, self.product) 

class WorksTestViewItemInline(admin.StackedInline):
    model = OrderItemWorksView
    #formset = MyInlineFormset # works
    extra = 0
    description = True
    #formfield_overrides = text_box(2, 150)
    verbose_name = '' # individual tabular title prefix
    classes = ['collapse']#, 'open'] # for collapse default open https://stackoverflow.com/questions/1766864/django-admin-add-collapse-to-a-fieldset-but-have-it-start-expanded
    #verbose_name_plural = 'modified plural'
    #autocomplete_fields = ('product',) # requires search_fields on the related object’s ModelAdmin
    fields = ('xnotes', tuple(work_field_names))#, 'amount') #('product','quantity'),
    #formset = forms.modelformset_factory(model, fields='__all__')
    rofields = []
    def get_readonly_fields(self, request, obj=None):
         return ['product','quantity','xnotes'] + self.rofields #,'product_notes'
    class Media:
        css = {'all': ('erp/inline.css',)} #'erp/hide_inline_title.css',
        #js = ('erp/collapse_open.js',)
    def has_add_permission(self, request, obj=None):
         return False
    def has_delete_permission(self, request, obj=None):
        return False
    def get_fieldsets(self, request, obj=None):    
        pass                                                                  
        return super().get_fieldsets(request, obj)  
    def get_queryset(self, request): 
        qs = super().get_queryset(request) #works
        self.verbose_name_plural = self.vnp
          #import pdb; pdb.set_trace()  
        return qs.filter(product__type__code=self.ttt) #e.g. 'CM'


class WorksTestPrintOrder(Order): 
    class Meta:
        proxy = True
   
@admin.register(WorksTestPrintOrder, site=site_proxy)
class WorksTestPrintAdmin(admin2):
    id_obj = None
    save_on_top = True
    #modify_labels = {'CCD_C':'Confirmed with Customer'}#, 'id': 'Order ID'} 
    listviewtitle = 'custom title - list view'
    ordertitle = True
    suppress_form_controls = {
        'show_save_and_add_another': False,
        'show_delete': False,
        'show_save': False,
    }

    list_display = ['id','company','MD','batch_info'] #'xbatch', 'confirmed']
    fields = ['xmanufacture_notes','xdelivery_notes'] # ('id','company', 'key_date') -> in page title
    def get_readonly_fields(self, request, obj=None):
        # why no error MD is readonly?
        default = ['batch_info','xmanufacture_notes','xdelivery_notes','created_at','modified','company']
        # if obj and obj.CCD_C:
        #     return default+['CCD_C']
        return default
    #date_hierarchy = 'LD'
    #id.short_description = 'Order ID'
    #list_filter = ['created_at', 'status']
    #search_fields = ['first_name', 'address']
    def get_inlines(self, request, obj):  
        acc = []
        #restrict to only show product_types defined in the order
        dd = obj.item.values_list('product__type__pk', flat=True).distinct()
        # create seperate inline for each product class (so we can format each row distinctly)
        for ptype in ProductType.objects.filter(pk__in = dd).all():
            # e.g. type('CM', (MOOrderItemInline,), {'ttt':'CM','vnp':"Changing Mats"})
            qq = type(
                ptype.code, (WorksTestViewItemInline,), 
                {'ttt':ptype.code,'vnp':ptype.title, 'rofields':ptype.workfields_not_defined}
                )
            acc.append(qq)
        return acc

    class Media:
        #extend = False
        css = {'screen': ('erp/hide_today.css', 'erp/label_width.css')} # not working
        #pass #js = ('erp/q.js',)
    #actions = [admin_order_shipped]
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


#------------MPrint --------------------


class MPrintOrder(Order): # allows to re-register model without error
    class Meta:
        proxy = True


class MPrintOOrderItemInline(admin.TabularInline):
    model = OrderItemWorksView
    extra = 0
    description = True
    verbose_name = '' # individual tabular title prefix
    fields = ('xproduct', 'quantity', 'xnotes', 'tally', 'total', 'printed')

    rofields = []
    def get_readonly_fields(self, request, obj=None):
         return ['xproduct','quantity','xnotes','total']# + self.rofields
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
        qs = super().get_queryset(request) #works
        self.verbose_name_plural = self.vnp
          #import pdb; pdb.set_trace()  
        return qs.filter(product__type__code__in=self.ttt) #'CM'
    def xproduct(self, obj): 
        #import pdb; pdb.set_trace() 
        if obj:
            batch_obj = obj.product
            ##url = reverse("admin:erp_batch_changelist")
            url = reverse(name_proxy +":erp_product_change", args=[batch_obj.id]) 
            #import pdb; pdb.set_trace() 
            return format_html('<a style="font-weight:bold" href="{}">{} </a>', url, batch_obj)
    def total(self, obj):
        total = 'error in tally'
        try:
            total = sumtally(obj.tally)
        except:
            pass
        return total


@admin.register(MPrintOrder, site=site_proxy)
class MPrintOrderAdmin(admin2):
    #relevantcodes = list(ProductType.objects.filter(print=True).values_list('code', flat=True))
    #import pdb; pdb.set_trace()
    id_obj = None
    save_on_top = True
    listviewtitle = 'custom title - list view' # place holder
    ordertitle = True
    suppress_form_controls = {
        'show_save_and_add_another': False,
        'show_delete': False,
        'show_save': False,
    }
    def get_list_display(self, obj):
        return ['id','company','MD','batch_info']

    fields = ['xmanufacture_notes','xdelivery_notes'] # ('id','company', 'key_date') -> in page title
    def get_readonly_fields(self, request, obj=None):
        default = ['batch_info','xmanufacture_notes','xdelivery_notes','created_at','modified','company']
        return default
    def get_inlines(self, request, obj):  
        #return [MPrintOOrderItemInline]
        return [type(
                "xxx", (MPrintOOrderItemInline,), 
                {'ttt':['CM','SPLASH'],'vnp':'Print Room'} # todo abstract
                )]
    class Media:
        pass #js = ('erp/q.js',)
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    def has_add_permission(self, request, obj=None):
         return False
    # def MD(self, obj):
    #     dd = None
    #     try:
    #         dd = obj.batchorder.batch.MD.strftime("%a %d %b")
    #     except:
    #         pass
    #     return dd
    #MD.admin_order_field = 'batchorder__batch__MD'
    def get_queryset(self, request): 
        qs = super().get_queryset(request) #works
        #import pdb; pdb.set_trace()  
        return qs.filter(item__product__type__print=True)#.distinct().all()
    #date_hierarchy = 'MD'
    def jobs_done(sel, obj):
        return 
    def jobs_todo(sel, obj):
        return 

#
# --------- ignore below -------------

#AuthorFormSet = forms.modelformset_factory(OrderItem_adminview, form=MOOrderItemInline)

#formset = forms.modelformset_factory(model, fields='__all__')

#prepopulated_fields = {"notes": ("office_notes",)} # keep example

# class MOrder(Order): # allows to re-register model, but gives warnings
#     class Meta:
#         proxy = True

 # def get_inlines(self, request, obj):  
    #     acc = []
    #     #restrict to only show product_types defined in the order
    #     dd = obj.item.filter(product__type__print = True).values_list('product__type__id', flat=True).distinct()
    #     # create seperate inline for each product class (so we can format each row distinctly)
    #     for ptype in ProductType.objects.filter(pk__in = dd).all():
    #         # e.g. type('CM', (MOOrderItemInline,), {'ttt':'CM','vnp':"Changing Mats"})
    #         #import pdb; pdb.set_trace()
    #         qq = type(
    #             ptype.code, (MPrintOOrderItemInline,), 
    #             {'ttt':ptype.code,'vnp':ptype.title, 'rofields':ptype.workfields_not_defined}
    #             )
    #         acc.append(qq)
    #     return acc


# for modelform, example
# name_of_field = forms.ModelChoiceField(queryset=Specialization.objects.all(), label='Specjalizacja')

# class MyInlineFormset(forms.BaseInlineFormSet): # works but get_queryset method easier 
#     # def __new__(cls,):
#     #     return super(MyInlineFormset, cls).__new__(cls)
#     def __init__(self, *args, **kwargs):
#         #ttt = kwargs['args1'] 
#         ttt = 'CM'
#         super().__init__(*args, **kwargs)
#         self.queryset = self.queryset.filter(product__type__code=ttt)


# class test2x(admin.StackedInline):
#     model = OrderItem_adminview
#     formset = MyInlineFormset # works
#     #formset = forms.modelform_factory(OrderItem_adminview, extra=0, fields = ('product_notes',))

# def formfield_for_dbfield(self, db_field, **kwargs):
    #     if db_field.name == 'notes':
    #         kwargs['initial'] = 'pppp'
    #     return super().formfield_for_dbfield(db_field, **kwargs)
    # def get_changeform_initial_data(self, request):
    #     return {'notes': 'custom_initial_value'}
    #formfield_overrides = {
       #models.IntegerField: {'widget': widgets.NumberInput(attrs={'size':'5'})},

"""