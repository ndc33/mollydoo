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
from ..models import BatchOrder, Batch, Container

from .setup import admin2, text_box
from .setup import erp_admin, site_proxy, name_proxy

from ..utils import setwidget


class ContainerOrderInline(admin.TabularInline):
    model = Order
    extra = 0
    #show_change_link = True
    #list_display = ('title', 'type', 'active')
    fields = ('order_link', 'company','OD','LD_markup','CD_markup')#,'container') # will not show container key
    readonly_fields=('order_link','id','company','OD','LD_markup','CD_markup') # 'id',
    class Media:
        css = {'all': ('erp/hide_inline_title.css', )}
    def has_add_permission(self, request, obj=None):
         return False
    def has_delete_permission(self, request, obj=None):
        return False
    def order_link(self, obj): 
        #import pdb; pdb.set_trace() 
        if obj:
            batch_obj = obj
            url = reverse(name_proxy +":erp_order_change", args=[batch_obj.id]) 
            return format_html('<a style="font-weight:bold" href="{}">{} </a>', url, batch_obj)
    


@admin.register(Container, site=site_proxy)
class ContainerAdmin(admin2):
    inlines = [ContainerOrderInline]
    suppress_form_controls = {
            'show_save_and_add_another': False,
            'show_save': False,
            #'show_delete': False
    }
    formfield_overrides = text_box(3, 70)
    



class BatchOrderInline(admin.TabularInline):
    model = BatchOrder
    extra = 0
    fields = ('order', 'company', 'CD_markup')
    class Media:
        css = {'all': ('erp/hide_inline_title.css', )}
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        if w:= form.base_fields.get('order'):
            setwidget(w.widget)
        return formset
        # https://groups.google.com/g/django-developers/c/10GP72w4aZs
        # from functools import partial
        # kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        # return super().get_formset(request, obj, **kwargs)
    def formfield_for_foreignkey(self, db_field, request, **kwargs): # in progress
        try: # todo try botch for add_item
            if db_field.name == "order":
                #import pdb; pdb.set_trace() 
                vv = int(request.resolver_match.kwargs['object_id'])
                #if vv:
                vv = vv or -1
                qq = Order.objects.filter(Q(batchorders__isnull = True) | Q(batchorders__batch = vv))
                kwargs["queryset"] = qq
        except:
            #kwargs["queryset"] = Order.objects.none() # added for fixed key 
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    def get_readonly_fields(self, request, obj=None):
        #if obj:
        return ('company','CD_markup',)
        #return ('order', 'company', 'CD_markup')
    # CD_C.boolean = True # keep info
    def order_link(self, obj): 
        #import pdb; pdb.set_trace() 
        if obj:
            url = reverse(name_proxy +":erp_order_change", args=[obj.order.id]) 
            return format_html('<a style="font-weight:bold" href="{}">{} </a>', url, obj.order)
    order_link.short_description = 'Order'


class BatchOrderInlineFixedKey(BatchOrderInline): # not used
    fields = ('order_link', 'company', 'CD_markup') # added
    readonly_fields = ('order_link', 'company', 'CD_markup',)
    def has_add_permission(self, request, obj=None):
        return False
    
class BatchOrderInlineFreeKey(BatchOrderInline): # not used
    pass
    verbose_name_plural = 'Add New Order Items'
    def get_queryset(self, request): 
        qs = super().get_queryset(request) 
        return qs.none()

    
@admin.register(Batch, site=site_proxy)
class BatchAdmin(admin2):
    list_display = ['title', 'DD', 'orders'] # 'num_orders','DD'] # 'CD', 'CD_C', 
    readonly_fields=('id','orders') #'num_orders')
   
    formfield_overrides = text_box(3, 70)
    fields = ['title', 'DD', 'notes']
    suppress_form_controls = {
            'show_save_and_add_another': False,
            'show_delete': False
    }
    class Media:
        css = {'all': ('erp/label_width.css', )}
    #id.short_description = 'Order ID'
   #  {
 #'classes': ('wide', 'extrapretty'),
 #}
    #list_filter = ['created_at', 'status']
    #search_fields = ['first_name', 'address']
    inlines = [BatchOrderInline]
    #inlines = [BatchOrderInlineFixedKey, BatchOrderInlineFreeKey]
    def orders(self, obj):
        qq = Order.objects.filter(batchorders__batch__pk = obj.id)# query
        return ['%s-%s'%(q.company.shortname, q.id) for q in qq]
   
  

   

# --------- ignore below -------------



@admin.register(BatchOrder, site=site_proxy) # only for exploration
class BatchOrderAdmin(admin2):
    model = BatchOrder
    extra = 0
    remove_pk_controls = ['batch', 'order']
    readonly_fields=('id', 'LD', 'xs1')
    fields = ('batch', ('order', 'xs1', 'LD'))
    list_display = ('order','batch')
    list_editable = ('batch',)
    list_display_links = None#('order',)
#     readonly_fields=('order', 'product', 'quantity')
    def formfield_for_foreignkey(self, db_field, request, **kwargs): # in progress
        if db_field.name == "order":
            try: # todo botch for add item bug
                vv = self.myobject_id = request.resolver_match.kwargs['object_id'] # gives <Order: #>.
                vv = vv or -1
                qq = Order.objects.filter(Q(batchorders__isnull = True) | Q(batchorders = vv))
                kwargs["queryset"] = qq
            except:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
"""
# class BatchOrderAdminForm(forms.ModelForm): 
#     class Meta:
#         model = BatchOrder
#         fields = '__all__' 
   
#     def __init__(self, *args, **kwargs):
#         #import pdb; pdb.set_trace()
#         # instance = kwargs.get('instance', None)
#         # if instance and instance.pk:
#         #     import pdb; pdb.set_trace()
#             #self.fields['order'].widget.attrs['readonly'] = True
    
#         #if kwargs.get('instance', None):
#         #    ppp = kwargs['instance']
#         # widgets = { # works
#         #     'notes': Textarea(attrs={'cols': 30, 'rows': 2}),
#         # }
#         super().__init__(*args, **kwargs)
#         instance = getattr(self, 'instance', None)
#         if instance and instance.pk:
#             pass #import pdb; pdb.set_trace()
#             #self.fields['order'].widget.attrs['readonly'] = True
# #self.fields['image'].widget.attrs['hidden'] = True # in forms init

 # def formfield_for_dbfield(self, db_field, **kwargs):
    #     if db_field.name == 'order':
    #         vv = self.myobject_id
    #         qq = Order.objects.filter(Q(batchorder__isnull = True) | Q(batchorder__batch = vv))
    #         kwargs["queryset"] = qq
    #         return db_field.formfield(**kwargs)
    #     return super().formfield_for_dbfield(db_field,**kwargs)

# class BatchAdminForm(forms.ModelForm): # system works well (not used)
#     class Meta:
#         model = Batch
#         fields = '__all__' 
#         # widgets = { # works
#         #     'notes': Textarea(attrs={'cols': 30, 'rows': 2}),
#         # }

#     #import pdb; pdb.set_trace()
#     #order_notes = forms.CharField(initial = 'readonly')
#     def __init__(self, *args, **kwargs):
#         #https://stackoverflow.com/questions/2988548/overriding-initial-value-in-modelform # works
#         try:
#             pass
#             # modelid =  kwargs['instance'].id
#             # vv = Order.objects.get(id=modelid)
#             # #import pdb; pdb.set_trace()
#             # initial = kwargs.get('initial', {})
#             # initial['notes'] = 'Test'
#             # kwargs['initial'] = initial
#         except:
#             pass
#         # try:
#         #     instance = getattr(self, 'instance', None)
#         #     if instance and instance.pk:
#         #         self.fields['sku'].widget.attrs['readonly'] = True
#         # except:
#         #     pass
#         super().__init__(*args, **kwargs)
#         self.fields['order'].widget.attrs['hidden'] = True 
#         #self.fields['notes'].label = 'My new label' # *this works for label
#         #self.fields['include_company_order_notes'].label = 'include?'
#         #self.fields['include_company_manufacture_notes'].label = 'include?'
#         #self.fields['include_company_delivery_notes'].label = 'include?'
#         #widget=forms.TextInput(attrs={'readonly':'readonly'})
#         # can only specify initial for unbound fields 
#         # widgets = {
#         #     'order_notes': forms.widgets.TextInput(attrs={'readonly':'readonly'}),
#         # }
#         #order_notes = forms.Textarea(
#         #    widget=forms.TextInput(attrs={'readonly':'readonly'}),)


# <<< container stuff - dead >>>

# class OrderInline(admin.TabularInline):
#     model = Order
#     extra = 0
#     #show_change_link = True
#     #list_display = ('title', 'type', 'active')
#     fields = ('id', 'company')
#     readonly_fields=('id','company')
#     class Media:
#         css = {'all': ('testingapp/hide_inline_title.css', )}


# @admin.register(Container, site=site_proxy)
# class ContainerAdmin(admin.ModelAdmin):
#     fields = ('title', ('PDD', 'CCD_C') )
#     inlines = [OrderInline]
#     pass
#admin.site.register(Container)

# class AddPriceListItemInline(admin.TabularInline): 
#     model = PriceListItem
#     extra = 0
#     #list_display = ('name', 'position')
#     #fields = ['name', 'role']
#     def has_change_permission(self, request, obj=None):
#         return False
#     # def has_delete_permission(self, request, obj=None):
#     #     return False
#     def has_view_permission(self, request, obj=None):
#         return False

# @admin.register(PriceList)
# class PriceListAdmin(admin.ModelAdmin):
#     inlines = [AddPriceListItemInline,]
#     pass
#     #list_display = ('title', 'type')

# @admin.register(PriceListItem)
# class PriceListItemAdmin(admin.ModelAdmin):
#     pass #list_display = ('title', 'type')

"""