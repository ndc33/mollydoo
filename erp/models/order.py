from django.db import models
from django.utils.html import format_html
from django.db.models import Q, F, Count, Sum, ExpressionWrapper, DecimalField, IntegerField
from django.forms.models import model_to_dict
import datetime
import operator
from decimal import Decimal

from .company import Company
from .product import ProductType, ProductDisplayCategory#ProductCategories
#from .batch import Container
from .orderitem import OrderItem
from ..utils import ss, work_field_names, decorate, sumtally, get_roll_groups, shortdate
from .specnotes import OrderNoteItem, OrderNoteAbstract

#from simple_history.models import HistoricalRecords
#from smart_selects.db_fields import ChainedForeignKey


# https://django-model-utils.readthedocs.io/en/latest/managers.html
#from model_utils.managers import InheritanceManager, QueryManager
#

class OrderTotalSummaryMethods():
    # '-' to not show misleading zero for a product for which process does not exist
    pass
   
# class OrderQuerySet(models.QuerySet):
#     def public_method(self):
#         return
#     def with_progress(self):
#         return (
#             self.annotate(qqq=models.Value('qqq annotation', output_field=models.CharField()))
#         )

class QRound(models.Func):
    # not working DB type issue??
    function = 'ROUND'
    #arity = 2
    template='%(function)s(%(expressions)s, 2)'

class OrderManager(models.Manager):
    ''' optimize queries with prefetches and annotations, (reduces queries by 1 order of magnitude)'''
    #use_for_related_fields = True
    # def get_queryset(self):
    #     return OrderQuerySet(self.model, using=self._db)
    def progress3(self, category):
        pass
    def get_queryset(self):
        from .product import ccc
        #categories = ccc('{category}')
        qs = super().get_queryset().prefetch_related(
            'items', 
            #'items__product', 
            #'items__product__type', 
            #'items__product__type__category',
            #Prefetch('books', queryset=Book.objects.filter(price__range=(250, 300))))
            #'items__product__productnotes'#, 'ordernoteitems'
        ).select_related(
            'company',
            'batch',
            #'items__product__type','items__product__type__category'
        ).annotate(
            ## items__product__type__category__title
            #**{f'sum_{category}':Sum('items__quantity', filter=Q(items__product__type__category__title=category)) 
            #    for category in categories}  
        ).annotate(
            # value_net2 works but issues with rounding and sum row
            value_net2 = QRound(Sum(F('items__xprice')*F('items__quantity')), output_field=DecimalField(decimal_places=2))
            #all_categories = 
            #order_total_quantity = Sum('items__quantity') 
        ).annotate(
            #**{f'remain_{category}_{process}':Sum(f'items__{process}_remain2', 
            # filter=Q(items__product__type__category__title=category))
            #    for category in categories for process in work_field_names}
        )
        #import pdb; pdb.set_trace()
        #qs = qs.annotate(qq2=models.Value('order qq2 annotation', output_field=models.CharField())) # testing
        return qs


def copy_and_create_order_notes(instance):
    company = Company.objects.get(id=instance.company_id)
    company_ordernotes = company.ordernotes.all()
    commonfields = OrderNoteAbstract._meta.fields
    for note in company_ordernotes:
        fields = model_to_dict(note, fields=[f.name for f in commonfields])
        #import pdb; pdb.set_trace()
        fields['order'] = instance
        OrderNoteItem.objects.create(**fields)
        #pp = OrderNoteItem(**fields)
        #pp.save()


class Order(models.Model, OrderTotalSummaryMethods):
    objects = OrderManager()
    id = models.AutoField(primary_key=True, verbose_name="Order") # get verbose name on ID - not required
    company = models.ForeignKey('Company', related_name='orders', on_delete=models.PROTECT)
    batch = models.ForeignKey('Batch', related_name='orders', default=1, null=True, blank = True, on_delete=models.SET_NULL)
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
    #notes = models.TextField(blank=True, default='')
    # x_ means copied over on creation
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        #ordering = ('LD',)
        #base_manager_name = 'objects'
        pass
    def save(self, *args, **kwargs):
        firsttime = False
        if self._state.adding is True:
            firsttime = True
            #import pdb; pdb.set_trace()
            self.OD = datetime.date.today()
        super().save(*args, **kwargs)
        if firsttime:
            copy_and_create_order_notes(self)
    @property        
    def str_id(self): # added to try to get around int error on search
        return '%s' % self.id      
    def __str__(self):
        return '%s %s' % (self.company.shortname, self.id)
    @property
    @decorate(admin_order_field = 'batch__dispatch_date')
    def DD(self):
        qq = getattr(self.batch, 'dispatch_date', None) # access issue just wierd
        return shortdate(qq)
    @property
    #@decorate(admin_order_field='status') # is required to return query
    def status(self):
        # just a crude mock-up for future functionality
        # note: need lots of data checking on inputs for incoherent combinations 
        status = 'Shelf' # means unassigned
        if getattr(self.batch, 'dispatch_date', None):
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
    @decorate(short_description = "LD", admin_order_field = 'LD')
    def LD_markup(self): # need to change format to differentiate this with undeline or such
        color = '8c8c8c' if not self.LD_S else '000000'
        return format_html('<span style="color: #{};">{}</span>', color, shortdate(self.LD))
    @property
    @decorate(short_description = "CD", admin_order_field = 'CD')
    def CD_markup(self):
        color = '8c8c8c' if not self.CD_C else '000000'
        return format_html(
            '<span style="color: #{};">{}</span>', color, shortdate(self.CD))
    @property
    @decorate(admin_order_field = 'value_net2') 
    def value_net(self):
        value = self.value_net2
        # value = OrderItem.objects.filter(order__id = self.id).aggregate(sum=Sum(
        #     F('xprice')*F('quantity'), output_field=DecimalField())
        #     )["sum"]
        return round(value, 2) if value else 0 
    def productcategoryprocess_remain(self, product_category, process, withtotals=False):
        '''basis for dynamic calling (see below) such as CM_total_all'''
        remain_total = qty_total = 0
        hasresult = False
        # the moral is never try to filter a prefetch!
        items = self.items.all()
        #items = self.items.filter(product__type__category__title = product_category) #product__type__category__title = 
        for item in items:
            if product_category == item.product.type.category.title: # use with .all()
                remain_subtotal = getattr(item, process + '_remain2') # _2 is the annotation
                qty_subtotal = item.quantity
                if isinstance(remain_subtotal, int):
                    remain_total += remain_subtotal
                    qty_total += qty_subtotal
                    hasresult = True
        if hasresult:
            if withtotals:
                #return '%s of %s' % (remain_total, qty_total) 
                return format_html('{} <span style="color: #{};"><sub>of {}</sub></span>', remain_total, '585858', qty_total)
            else: 
                return remain_total 
        return '-'
    def productcategoryprocess_remain_qs(self, product_category, process, withtotals=False):
        # ** dog slooowwww **
        # OrderItem.objects ; .select_related('product__type__category')
        qs = OrderItem.objects.filter(
            Q(order__id = self.id) & # not required with  self.items
            Q(product__type__category__title=product_category) #product__type__category__title -> using category annotation same speed
            ).all()
        remain_total = qs.aggregate(sum=Sum(F(f'{process}_remain2'), 
                output_field=IntegerField()))['sum']
        qty_total = qs.aggregate(qty=Sum(F('quantity'), 
                output_field=IntegerField()))['qty']
        if remain_total is None:  # distiguish from zero 
            return '-'
        if withtotals: 
            #return '%s of %s' % (remain_total, qty_total) 
            return format_html('{} <span style="color: #{};"><sub>of {}</sub></span>', remain_total, '585858', qty_total)
        else: 
            return remain_total 
    def productcategory_quantity(self, product_category, withprogress=False):
        '''basis for dynamic calling e.g. CM_remain_weld  or (with progress) ARM_progress_all'''
        total_quantity = total_progress = hasresult = 0
        #items = self.items.filter(product__type__category__title=product_category)#.all()
        for item in self.items.all(): # filtering items destroy prefetch
            #import pdb; pdb.set_trace()
            if product_category == item.product.type.category.title: #kk
                qty = item.quantity
                total_quantity += qty
                # swapped for annotation _2 25/03 - TODO review the whole subroutine
                total_progress += item.progress2 * qty #item.item_progress * qty
                hasresult = True
        if hasresult:
            total_progress = total_progress/total_quantity if total_quantity else ''
            if withprogress:
                #return '%s of %s' % (total_quantiy, total_progress)
                total_progress = '{0:.0f}%'.format(total_progress) #if total_progress else '0%'
                return format_html('{} <span style="color: #{};">&nbsp<sub>{}</sub></span>', total_quantity, '585858', total_progress)
            return total_quantity
        return '-'
   
 
