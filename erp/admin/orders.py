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

from ..models import Product, Order, OrderItem, ProductType

from .setup import erp_admin, site_proxy, name_proxy
from .setup import admin2, text_box

from ..utils import ss, setwidget, work_field_names

# TODO 
# html view for printing quotes, sales-orders and delivery-notes
#   (these documents are near identical) 
#   -> need to be able to edit the delivery address on the delivery note (drop ships)
# company model address links will likely change to individual fixed links 
#   (current poor method to explore sublistings for drop ships) 
#
# uploaded files (products mainly - but accessed from orderitems)
#   include image for art files (reduced image to identify products only)
#   A4 product label artwork, printed from the erp, by workers
#   similiar barcode-image files to print on label printers
#   pdf or image files which serve as specification/construction info  

@admin.register(ProductType, site=site_proxy)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['code'] + work_field_names # ('__all_',) for info
    readonly_fields = ('id',)
    class Meta:
        pass
        # widgets = {
        #     'id_code': forms.TextInput(attrs={'class': 'label_width.css'}),
        # }
    class Media:
       css = {'all': ('erp/label_width.css', )}


class TemplateFilter(admin.SimpleListFilter): # needs further work
    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        types = qs.values_list(self._lookup,self._lookup )
        return list(types.order_by(self._lookup).distinct())
    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(**{self._lookup : self.value()}) # note the trick

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
    list_display = ('title', 'type', 'price', 'company', 'active') 
    save_as = True
    list_filter = (ProductTypeFilter, ProductCompanyFilter)
    formfield_overrides = text_box(3, 70)
    remove_pk_controls = ['company', 'type']
 


class OrderItemAdminView(OrderItem):
    class Meta:
        proxy = True
    # def __str__(self):
    #     return '%s of %s' % (self.quantity, self.product)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class OrderItemInline(admin.TabularInline):
#class OrderItemInline(admin.StackedInline):
    model = OrderItemAdminView
    extra = 0
    formfield_overrides = text_box(1, 30)
    fields = ('product','xnotes', 'xprice','quantity')
    #fields = (('product', 'xprice','quantity'),('xprint_notes','xcut_notes','xpack_notes'))
    class Media:
        css = {'all': ('erp/hide_inline_title.css', )}
    myobject_id = None
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        if w:= form.base_fields.get('product'):
            setwidget(w.widget)
        return formset
    # def price(self, obj):
    #     #return OrderItem.objects.get(id=obj.id)
    #   return obj.product.price
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        try: # todo (botch for add view bug)
            if db_field.name == "product":
                self.myobject_id = request.resolver_match.kwargs['object_id'] # gives <Order: #>.
                if self.myobject_id:
                    companyid = Order.objects.get(pk=self.myobject_id).company_id
                    #import pdb; pdb.set_trace()
                    kwargs["queryset"] = Product.objects.filter(company__pk = companyid)
        except:
            kwargs["queryset"] = Product.objects.none() # why none instead of default all?
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    #def save(self, commit=True):
    #    title = self.cleaned_data.get('product')
    #    return super().save(commit=commit)

class OrderItemInlineFixedKey(OrderItemInline):
    pass
    fields = ('link_product','xnotes', 'xprice','quantity') # added
    readonly_fields = ('link_product',)
    def has_add_permission(self, request, obj=None):
         return False
    def link_product(self, obj): 
        #import pdb; pdb.set_trace() 
        if obj:
            url = reverse(name_proxy +":erp_product_change", args=[obj.product.id]) 
            return format_html('<a style="font-weight:bold" href="{}">{} </a>', url, obj.product)
    link_product.short_description = 'Product'

class OrderItemInlineFreeKey(OrderItemInline):
    pass
    verbose_name_plural = 'Add New Order Items'
    def get_queryset(self, request): 
        qs = super().get_queryset(request) #works
        #self.verbose_name_plural = self.vnp
          #import pdb; pdb.set_trace()
        #qs=qs.none()
        return qs.none()#qs#qs.filter(product__type__code=self.ttt) #'CM'
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        if w:= form.base_fields.get('product'):
            w.widget.can_change_related = False
            w.widget.can_delete_related = False
            w.widget.can_add_related = True
            #setwidget(w.widget)
        return formset



@admin.register(Order, site=site_proxy)
class OrderAdmin(admin2):
    #form = OrderAdminForm # example
    save_on_top = True
    remove_pk_controls = ['company']
    modify_labels = {'CD_C':'', 'LD_S':''}#, 'id': 'Order ID'}
    listviewtitle = 'custom title - list view'
    formfield_overrides = text_box(3, 70)
    suppress_form_controls = {
        'show_save_and_add_another': False,
        'show_delete': False,
        'show_save': False
    }
    list_display = ['id','company','OD','LD_markup','CD_markup', 'DD','batch_name','status'] 
    fields = [
        ('id', 'delivered', 'invoiced', 'paid'),
        'company',
        ('OD','LD','LD_S'),
        ('CD', 'CD_C','batch_info','container'),  
        'notes','xorder_notes','xmanufacture_notes','xdelivery_notes',
    ]
    #search_fields = ['foreign_key__related_fieldname'] # example - note the db field follow!
    inlines = [OrderItemInlineFixedKey, OrderItemInlineFreeKey]#[OrderItemInline]
    class Media:
        #extend = False # keep for info, default True
        #css = {'screen': ('erp/hide_today.css', 'erp/label_width.css')} # not working?
        css = {'screen': ('erp/admin_order.css',)}
        pass #js = ('erp/q.js',)
    #actions = [admin_order_shipped]
    def get_readonly_fields(self, request, obj=None):
        default = ['id','batch_info','batch_name','DD','created_at','modified','status','xs1','LD_markup','CD_markup']#'id',
        #import pdb; pdb.set_trace()
        if obj: # existing record
            return default+['company']
        #self.autocomplete_fields = ['company'] # attempted hack
        return default # object creation
    

# ----------- for testing only------

class temp(OrderItem):
    class Meta:
        proxy = True
        verbose_name_plural = 'Test Order Items View'

class OrderItemOrderFilter(TemplateFilter): 
    title = 'Order'
    parameter_name = 'order'
    _lookup = 'order'

class OrderItemTypeFilter(TemplateFilter): 
    title = 'Type'
    parameter_name = 'type'
    _lookup = 'product__type__code'

class OrderItemBatchFilter(admin.SimpleListFilter): # todo (none's not working)
    title = 'Batch'
    parameter_name = 'batch'
    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        types = qs.values_list('order__batchorders__batch__title','order__batchorders__batch__title')
        return list(types.order_by('order__batchorders__batch').distinct())
    def queryset(self, request, queryset):
        if self.value() is None:
            # todo return modified default filter set
            # return queryset.filter(state__complete=True)
            return queryset
        return queryset.filter(order__batchorders__batch__title=self.value())


@admin.register(temp, site=site_proxy)
class OrderItemAdmin(admin2):
    # todo model-specific queryset with named annotations to prevent further queries? e.g.
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.annotate(
    #     _order_ref=Count("hero", distinct=True),
    #     #_villain_count=Count("villain", distinct=True),
    #     )
    #     return queryset
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    wft = [wfd + '_tallytotal' for wfd in work_field_names]
    list_display = ('product','quantity','norder',*wft) # work_field_names
    list_per_page = 50
    list_filter = (OrderItemTypeFilter, OrderItemOrderFilter, OrderItemBatchFilter)
    producttitle = True
    suppress_form_controls = {
        'show_save_and_add_another': False,
        'show_delete': False,
        'title': 'Change this for a custom title.'
    }
    # def get_fields(self, request, obj=None):
    #     wf = OrderItem.objects.get(id = obj.id).work_fields
    #     return (('company','norder','batch'),'order_notes','xnotes',*wf)
    # def get_readonly_fields(self, request, obj=None):
    #     default = ('company','product','quantity','norder',
    #                     'order_notes','work_fields','batch')
    #    return default
    class Media:
        css = {'all': ('erp/label_width.css', )}
    class Meta:
        pass #verbose_name_plural = 'Test Order Items View'
   


# --------- ignore below -------------

# NOTE's
# look at autocomplete_fields = instead of raw_id_fields
# get_form 
    # get rid of annoying change etc icons acting on related models next to primary key
    # for improved alternative? see https://matthewdowney.github.io/django-modify-admin-form-from-request.html
#  get_formset 
    # #https://stackoverflow.com/questions/26425818/django-1-7-removing-add-button-from-inline-form/37558444#37558444
    #"""
    #Override the formset function in order to remove the add and change buttons beside the foreign key pull-down
    # menus in the inline.
    #"""
# TODO's
# get_form -> generalize
# https://github.com/django/django/blob/master/django/contrib/admin/options.py (source)

    #raw_id_fields = ['product']
    #autocomplete_fields = ('product',) # requires search_fields on the related object’s ModelAdmin todo

# admin.RelatedOnlyFieldListFilter

# list_filter = ('product__type__code', )#'order', 'order__batchorder__batch') # does not filter relevent items
#if you need to specify this list dynamically, implement a get_sortable_by() method

 # # fieldsets = (
    #     ('example', {
    #         'classes': ('extrapretty', 'wide',),
    #         'fields': (('name', 'shortname'), ('type', 'status'), ('VAT_Number', 'tax_status'), 'office_notes', ('created_at', 'modified')),
    #     }),
    #     )

# class xForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         #if self.instance.order.customer:
#         self.fields['product'].queryset = Product.objects.filter(company=self.instance.order.company)
#         #self.instance.cities.all()

# def unpack(obj): # not used
#     for x in obj:
#         if isinstance(x, str):
#             yield x
#         elif isinstance(x, tuple):
#             yield from unpack(x)
#         else:
#            raise TypeError

# def batch(self, obj): # now use the model property -> keep
    #     if obj:
    #         batch_obj = obj.batchorders.batch
    #         ##url = reverse("admin:erp_batch_changelist")
    #         url = reverse(name_proxy +":erp_batch_change",  args=[batch_obj.id]) 
    #         ##return obj.batchitem.batch
    #         return format_html('<a style="font-weight:bold" href="{}">{} </a>', url, batch_obj)
    #batch.admin_order_field = 'batchorders__batch__dispatch_date'
    #batch.empty_value_display = 'SHELF' # not working
    #.short_description = "only for admin functions!"

#class Meta:
        # widgets = {
        #     'company': forms.TextInput(attrs={'class': 'myfieldclass'}),
        # }
#        pass
    # widgets = { # example only
    #     'company': widgets.TextInput(attrs = {
    #         'placeholder': 'Ingrese el contacto',
    #         'class': 'form-control',
    #         'data-validation': 'custom',
        #     })}


"""
# model form inheritance can be used for attaching unbound (non model) fields + many other functionality
.modelform
system works well
used in investigation for purpose of locking the foreign key references and other mods
class OrderAdminForm(forms.ModelForm): 
    # xnotes = forms.CharField(
    #     max_length=200,
    #     #required=False,
    #     help_text='Use puns liberally',
    #     initial = 'jj'
    # )
    #dummy = forms.CharField() keep example
    class Meta:
        model = Order
        fields = xfields2 #+['dummy']  #'__all__' #[f.name for f in Order._meta.fields]
        # widgets = { # works
        #     'notes': Textarea(attrs={'cols': 30, 'rows': 2}),
        # }

    def __init__(self, *args, **kwargs): # works
        #https://stackoverflow.com/questions/2988548/overriding-initial-value-in-modelform 
        try:
            pass
            # modelid =  kwargs['instance'].id
            # vv = Order.objects.get(id=modelid)
            # #import pdb; pdb.set_trace()
            # initial = kwargs.get('initial', {})
            # initial['notes'] = 'Test'
            # kwargs['initial'] = initial # very interesting
        except:
            pass
        super().__init__(*args, **kwargs) # some changes required before, some after __init__
        try:
            pass
            #import pdb; pdb.set_trace()
            #instance = getattr(self, 'instance', None)
            # if instance and instance.pk:
            #     self.fields['company'].widget.attrs={'readonly':'readonly'} # True
        except:
            pass
        # self.fields['notes'].label = 'My new label' # keep *this works for label
        # can only specify 'initial' for unbound fields?
"""
