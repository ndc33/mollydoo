from django import forms
from django.db import models
from django.db.models import Q, F, Count, Avg
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
#from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

#from simple_history.admin import SimpleHistoryAdmin

from ..models import Order, OrderItem
from ..models import ProductType,  Product

from .setup import erp_admin, site_proxy, name_proxy
from .setup import text_box
from .setup import product_link, company_link, container_link
from .workstemplate import TemplateFilter, admin2

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


class OrderItemAdminView(OrderItem):
    class Meta:
        proxy = True
        verbose_name = 'Order Item'
    # def __str__(self):
    #     return '%s of %s' % (self.quantity, self.product)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class OrderItemInline(admin.TabularInline):
#class OrderItemInline(admin.StackedInline):
    model = OrderItemAdminView
    extra = 0
    formfield_overrides = text_box(1, 30)
    fields = ('product','xnotes','xprice','quantity')
    #fields = (('product', 'xprice','quantity'),('xprint_notes','xcut_notes','xpack_notes'))
    class Media:
        css = {'all': ('erp/hide_inline_title.css', )}
    myobject_id = None
    # def get_formset(self, request, obj=None, **kwargs):
    #     formset = super().get_formset(request, obj, **kwargs)
    #     form = formset.form
    #     if w:= form.base_fields.get('product'):
    #         setwidget(w.widget)
    #     return formset
    # def price(self, obj):
    #     #return OrderItem.objects.get(id=obj.id)
    #   return obj.product.price
    """ broken
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        try: # todo (botch for add view bug)
            import pdb; pdb.set_trace()
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
    """
    #def save(self, commit=True):
    #    title = self.cleaned_data.get('product')
    #    return super().save(commit=commit)

class OrderItemInlineFixedKey(OrderItemInline):
    pass
    fields = ('product_link','xnotes','xprice','quantity') # added
    readonly_fields = ('product_link',)
    def has_add_permission(self, request, obj=None):
         return False
    def product_link(self, obj): 
        #import pdb; pdb.set_trace() 
        return product_link(obj.product)

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
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # moved from OrderItemInline
        try: # todo (botch for add view bug)
            #import pdb; pdb.set_trace()
            if db_field.name == "product":
                obj_id = request.resolver_match.kwargs['object_id'] # gives <Order: #>.
                if obj_id:
                    companyid = Order.objects.get(pk=obj_id).company_id
                    #import pdb; pdb.set_trace()
                    kwargs["queryset"] = Product.objects.filter(company__pk = companyid)
        except:
            kwargs["queryset"] = Product.objects.none() # why none instead of default all?
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(Order, site=site_proxy)
class OrderAdmin(admin2):
    #form = OrderAdminForm # example
    save_on_top = True
    remove_pk_controls = ['company','container']
    autocomplete_fields = ['company','container']
    search_fields = ['company__name','id','container__title',
            'items__product__title','items__product__type__title'] #'items__product__code'
    # change_list_template = 'change_list_totals.html'

    # def get_changelist(self, request, **kwargs):
    #     return ChangeListTotals
    # def get_search_results(self, request, queryset, search_term):
    #     queryset, use_distinct = super().get_search_results(request, queryset, search_term)
    #     try:
    #         search_term_as_int = int(search_term)
    #     except ValueError:
    #         pass
    #     else:
    #         queryset |= self.model.objects.filter(age=search_term_as_int)
    #     return queryset, use_distinct
    modify_labels = {'CD_C':'', 'LD_S':''}#, 'id': 'Order ID'}
    listviewtitle = 'Orders'
    formfield_overrides = text_box(3, 70)
    suppress_form_controls = {
        'show_save_and_add_another': False,
        'show_delete': False,
        'show_save': False
    }
    list_display = ['id','company_link','value_net','OD','LD_markup','CD_markup','container_link','status'] 
    #list_totals = [('items__xprice', Avg)]
    totalsum_list = ['value_net']
    unit_of_measure = '&pound;' # todo need prefix
    fields = [
        ('id', 'delivered', 'invoiced', 'paid'),
        'company',
        ('OD','LD','LD_S'),
        ('CD', 'CD_C','container'),  
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
        default = ['id','DD','created_at','modified','status','xs1','LD_markup','CD_markup','container_link','company_link']#'id',
        #import pdb; pdb.set_trace()
        if obj: # existing record
            return default+['company']
        #self.autocomplete_fields = ['company'] # attempted hack
        return default # object creation
    def container_link(self, obj): 
        if obj:
            return container_link(obj.container)
    #container_link.short_description = 'Container'
    def company_link(self, obj): 
        if obj:
            return company_link(obj.company)
    def value_net(self, obj):
        return '£%s' % obj.value_net
    

