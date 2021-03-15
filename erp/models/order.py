from django.db import models
from django.utils.html import format_html
from django.db.models import Q, F, Count, Sum, DecimalField
import datetime
import operator

from .company import Company
from .product import ProductType, ProductCategories
#from .batch import Container
from .orderitem import OrderItem
from ..utils import ss, work_field_names, decorate, sumtally, get_roll_groups, shortdate

#from simple_history.models import HistoricalRecords
#from smart_selects.db_fields import ChainedForeignKey


# https://django-model-utils.readthedocs.io/en/latest/managers.html
#from model_utils.managers import InheritanceManager, QueryManager

#

class OrderTotalSummaryMethods():
    # '-' to not show misleading zero for a product for which process does not exist
    pass
   

class OrderManager(models.Manager):
    ''' optimize queries with prefetches and annotations, (reduces queries by 1 order of magnitude)'''
    def get_queryset(self):
        qs =  super().get_queryset()
        #qs = qs.select_related('container')
        #qs = qs.select_related('batch')
        #all_product_types_defined = ProductType.objects.values_list('code', flat=True)
        ###all_product_types_defined = ProductType.objects.values('code')
        ###qs = qs.annotate(all_product_types_defined=all_product_types_defined)
        #qs = qs.annotate(_ppp=models.Value('ppp annotation', output_field=models.CharField())) # testing
        qs = qs.prefetch_related('items__product', 'items__product__type', 'items__product__type__category')#items__product__type
        # 'item', 'item__product' makes no difference
        return qs



class Order(models.Model, OrderTotalSummaryMethods):
    objects = OrderManager()
    sentinal_text = "---press update to copy STD notes---"
    id = models.AutoField(primary_key=True, verbose_name="Order") # get verbose name on ID - not required
    company = models.ForeignKey('Company', related_name='orders', on_delete=models.PROTECT)
    container = models.ForeignKey('Container', related_name='orders', default=1, null=True, blank = True, on_delete=models.SET_NULL)
    #active = models.BooleanField(default=True)
    OD = models.DateField(auto_now_add=False, blank=True, null=True)#, verbose_name="Order Date")
    LD = models.DateField(auto_now_add=False, blank=True, null=True)#, verbose_name="Lead Date")
    LD_S = models.BooleanField(default=False, help_text="Strict") # verbose_name="Lead Date Strict",
    CD = models.DateField(auto_now_add=False, blank=True, null=True)
    CD_C = models.BooleanField(default=False, help_text='confirmed')
    # these are just place-holders/demo's for future functionality (Delivery note scans, invoice number etc)
    delivered = models.BooleanField(default=False)
    invoiced = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')
    # x_ means copied over on creation
    xorder_notes = models.TextField(blank=True, default=sentinal_text)
    xmanufacture_notes = models.TextField(blank=True, default=sentinal_text)
    xdelivery_notes = models.TextField(blank=True, default=sentinal_text)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('LD',)
    def save(self, *args, **kwargs):
        #try:
        if self._state.adding is True:
            #import pdb; pdb.set_trace()
            company = Company.objects.get(id=self.company_id)
            if self.xorder_notes == self.sentinal_text:
                self.xorder_notes = company.order_notes
            if self.xmanufacture_notes == self.sentinal_text:
                self.xmanufacture_notes = company.manufacture_notes
            if self.xdelivery_notes == self.sentinal_text:
                self.xdelivery_notes = company.delivery_notes
            #if not self.id: # what?
            self.OD = datetime.date.today()
        #except:
        #    pass
        super().save(*args, **kwargs)
    def __str__(self):
        return '%s %s' % (self.company.shortname, self.id)
    @property
    @decorate(admin_order_field = 'container__dispatch_date')
    def DD(self):
        qq = getattr(self.container, 'dispatch_date', None) # access issue just wierd
        return shortdate(qq)
    @property
    #@decorate(admin_order_field='status') # is required to return query
    def status(self):
        # just a crude mock-up for future functionality
        # note: need lots of data checking on inputs for incoherent combinations 
        status = 'Shelf' # means unassigned
        if getattr(self.container, 'dispatch_date', None):
            status = 'Assigned'
        if self.delivered:
            status = 'delivered'
        if self.invoiced:
            status = 'invoiced'
        if self.paid:
            status = 'paid'
        return status
    @property
    def products_allowed(self):
        return self.company.own_products
    @property
    @decorate(short_description = "LD")
    def LD_markup(self): # need to change format to differentiate this with undeline or such
        color = '8c8c8c' if not self.LD_S else '000000'
        return format_html('<span style="color: #{};">{}</span>', color, shortdate(self.LD))
    @property
    @decorate(short_description = "CD")
    def CD_markup(self):
        color = '8c8c8c' if not self.CD_C else '000000'
        return format_html(
            '<span style="color: #{};">{}</span>', color, shortdate(self.CD))
    def productcategory_quantity(self, product_category, withprogress=False):
        '''basis for enumerated method generation (see below) such as CM_remain_weld 
            or (with progress) ARM_progress_all'''
        # core of this could be done directly on query (not worth effort)
        total_quantity = total_progress = hasresult = 0
        for item in self.items.all():
            #import pdb; pdb.set_trace()
            if product_category == item.product.type.category.title: #kk
                qty = item.quantity
                total_quantity += qty
                total_progress += item.item_progress * qty
                hasresult = True
        if hasresult:
            total_progress = total_progress/total_quantity if total_quantity else ''
            if withprogress:
                #return '%s of %s' % (total_quantiy, total_progress)
                total_progress = '{0:.0f}%'.format(total_progress) #if total_progress else '0%'
                color = '585858'
                return format_html('{} <span style="color: #{};">&nbsp<sub>{}</sub></span>', total_quantity, color, total_progress)
            return total_quantity
        return '-'
    def productcategoryprocess_remain(self, product_category, process, withtotals):
        '''basis for enumerated method generation (see below) such as CM_total_all'''
        remain_total = qty_total = 0
        hasresult = False
        for item in self.items.all():
            if product_category == item.product.type.category.title: #kk
                remain_subtotal = getattr(item, process + '_remain')
                qty_subtotal = item.quantity
                if isinstance(remain_subtotal, int):
                    #print(product_category, process, subtotal)
                    remain_total += remain_subtotal
                    qty_total += qty_subtotal
                    hasresult = True
        if hasresult:
            if withtotals:
                #return '%s of %s' % (remain_total, qty_total) 
                color = '585858'
                return format_html('{} <span style="color: #{};"><sub>of {}</sub></span>', remain_total, color, qty_total)
            else: 
                return remain_total 
        return '-'
    def cm_total(self): # just playing
        return self.productcategory_quantity('CM')
    @property
    def value_net(self):
        value = OrderItem.objects.filter(order__id = self.id).aggregate(sum=Sum(
            F('xprice')*F('quantity'), output_field=DecimalField())
            )["sum"]
        return round(value, 2)
   
    
# -----

def product_process_class_methods(cls, product_category, process, method_name, withtotals=False):
    def innerfunc(self):
        return self.productcategoryprocess_remain(product_category, process, withtotals)
    innerfunc.__name__ = method_name
    setattr(innerfunc, 'short_description', product_category)
    setattr (cls, innerfunc.__name__, property(innerfunc))
for process in work_field_names:
    ''' create methods e.g. CM_remain_weld'''
    for product_category in ProductCategories: 
        method_name = product_category + '_remain_' + process
        product_process_class_methods(Order, product_category, process, method_name, True)
######
for process in work_field_names:
    #  # crude and inefficient hack implimented
    ''' create methods e.g. CM_remain_weld_totals for the total summary row'''
    for product_category in ProductCategories: 
        method_name = product_category + '_remain_' + process +'_totals'
        product_process_class_methods(Order, product_category, process, method_name, False)

#---

def product_total_class_methods(cls, product_category, method_name, withprogress=False):
    def innerfunc(self):
        return self.productcategory_quantity(product_category, withprogress)
    innerfunc.__name__ = method_name
    setattr(innerfunc, 'short_description', product_category) 
    setattr (cls, innerfunc.__name__, property(innerfunc))
for product_category in ProductCategories: 
    '''e.g. ARM_total_all'''
    method_name = product_category + '_total_all'
    product_total_class_methods(Order, product_category, method_name, False)
for product_category in ProductCategories: 
    '''e.g. ARM_progress_all'''
    method_name = product_category + '_progress_all'
    product_total_class_methods(Order, product_category, method_name, True)
#######
for product_category in ProductCategories: 
    # crude and inefficient hack implimented
    '''e.g. ARM_progress_all_totals for the total summary row'''
    method_name = product_category + '_progress_all_totals'
    product_total_class_methods(Order, product_category, method_name, False)
    
