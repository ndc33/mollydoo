from django.db import models
from django.utils.html import format_html
import datetime

from .company import Company
#from .batches import Container
from ..utils import ss, work_field_names, decorate, sumtally, get_roll_groups


class OrderItemTotalSummaryMethods():
    ''' get the totals from sumtally for each process for the given orderitem, method = <process>_total'''
    # '-' to not show misleading zero for a product for which process does not exist
    # '-' logic is now twisted with downstream functions,  maybe redesign
    @property
    @decorate(short_description = "Printed") # changed to distinguish in ops views
    def print_tallytotal(self):
        if self.product.type.print:
            # this is unique to print (to track locations of print)
            roll_data = get_roll_groups(self.tally_print)
            return roll_data[0] # todo find a way to display roll totals 
        return '-'
    @property
    def print_locations(self):
        # only used by processes downstream of print
        roll_data = get_roll_groups(self.tally_print)
        return roll_data[1] 
    @property
    @decorate(short_description = "Cut")
    def cut_tallytotal(self):
        if self.product.type.cut:
            return sumtally(self.tally_cut)
        return '-'
    @property
    @decorate(short_description = "Weld")
    def weld_tallytotal(self):
        if self.product.type.weld:
            return sumtally(self.tally_weld)
        return '-'
    @property
    @decorate(short_description = "Stuff")
    def stuff_tallytotal(self):
        if self.product.type.stuff:
            return sumtally(self.tally_stuff)
        return '-'
    @property
    @decorate(short_description = "Pack")
    def pack_tallytotal(self):
        if self.product.type.pack:
            return sumtally(self.tally_pack)
        return '-'
    @property
    @decorate(short_description = "progress")
    def item_progress(self): 
        # needs more work
        total = 0
        count = 0
        for wf in self.work_fields:
            subtotal = getattr(self, wf+'_total')
            #if isinstance(subtotal, int):
            count+=1
            total += subtotal 
        if count:
            progress = total*100/count/self.quantity # %
        return round(progress,0) if count else '-'

    # @property
    # def product_notes(self):
    #     return self.product.notes


class OrderItemRemaingMethods():
    @property
    @decorate(short_description = "print")
    def print_remain(self):
        if self.product.type.print:
            return self.quantity - self.print_total
        return '-'
    @property
    @decorate(short_description = "cut")
    def cut_remain(self):
        if self.product.type.cut:
            return self.quantity - self.cut_total
        return '-'
    @property
    @decorate(short_description = "weld")
    def weld_remain(self):
        if self.product.type.weld:
            return self.quantity - self.weld_total
        return '-'
    @property
    @decorate(short_description = "stuff")
    def stuff_remain(self):
        if self.product.type.stuff:
            return self.quantity - self.stuff_total
        return '-'
    @property
    @decorate(short_description = "pack")
    def pack_remain(self):
        if self.product.type.pack:
            return self.quantity - self.pack_total
        return '-'
    

class OrderItemRelatedModelMethods():
    ''' info from other models required for views,
    the methods below which call other models 'calculated-properties' will inherit ordering and try/except protection'''
    @property
    def company(self):
        return self.order.company
    @property
    def order_notes(self):
        return '%s' % (self.order.notes)
    @property
    def products_allowed(self):
        return self.order.products # self.order.company.own_products 
    @property
    def work_fields(self):
        return self.product.type.workfields_defined
    @property
    def batch_info(self):
        return self.order.batch_info
    @property
    def batch(self):
        return self.order.batch 
    @property
    def batch_name(self):
        return self.order.batch_name
    @property
    def DD(self):
        return self.order.DD
    @property
    @decorate(admin_order_field='order__id')
    def norder(self):
        try:
            dd = self.order.id 
        except:
            dd = None
        return dd
    @property
    def overprint(self):
        '''only called by works-print-view'''
        return self.product.overprint


class OrderItemManager(models.Manager):
    ''' optimize queries with prfetches and annotations'''
    # modest improvement
    def get_queryset(self):
        qs =  super().get_queryset()
        qs = qs.annotate(_ppp=models.Value(1, output_field=models.IntegerField())) # testing
        ###qs = qs.prefetch_related(models.Prefetch('order__DD'))
        qs = qs.select_related('order__batchorders__batch')
        qs = qs.select_related('product__type')
        return qs



class OrderItem(models.Model, OrderItemRelatedModelMethods, OrderItemTotalSummaryMethods, OrderItemRemaingMethods):
    #
    objects = OrderItemManager()
    order = models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', related_name='items', on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(default=1)
    # x_ means copied over on creation
    xprice = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    xnotes = models.TextField(blank=True, default='')
    xprint_notes = models.TextField(blank=True, default='', help_text='xPrint Notes')
    xcut_notes = models.TextField(blank=True, default='')
    xpack_notes = models.TextField(blank=True, default='')
    # text field to hold the process tallies e.g. '3,7,23' parsed/summed into to <process>_total methods above
    tally_print = models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_cut = models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_weld = models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_stuff = models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_pack = models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    #
    print_total = models.PositiveSmallIntegerField(default=0, verbose_name='done')#blank=True, null=True)
    cut_total = models.PositiveSmallIntegerField(default=0)#blank=True, null=True)
    weld_total = models.PositiveSmallIntegerField(default=0)#blank=True, null=True)
    stuff_total = models.PositiveSmallIntegerField(default=0)#blank=True, null=True)
    pack_total = models.PositiveSmallIntegerField(default=0)#blank=True, null=True)
    # TODO need to remove and make this a writable form field?
    item_complete = models.BooleanField(default=False) # messy
    #
    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['order', 'product'], name='unique_order_item')
        ]
   
    def ppp(self): # test of qs annotations
        #import pdb; pdb.set_trace() 
        return self._ppp
    def __str__(self):
        return '%s' % self.id
    def save(self, *args, **kwargs):
        if self._state.adding is True:  #if not self.id: 
            # pre form-filling wont work if we do not have FK already saved
            # this is safe from cross-user-saving since only triggered on creation 
            try:
                self.xprice = self.product.price
                self.xnotes = self.product.notes
            except:
                pass
        else:
            pass
         
        super().save(*args, **kwargs)


# class OrderQuerySet(models.QuerySet):
#     def DD(self):
#         return (
#             self
#             .annotate(
#                 count_category=Count(
#                     'items__product__category'
#                 )
#             )
#             .filter(count_category__gt=1)
#         )
# rewriting query actually works (tested from pdb) KEEP
            # vv = OrderItem.objects.get(id=self.id)
            # vv._ppp = vv._ppp+2
# Articles.objects.annotate(blog_name=F('blog__name')).first() one of few examples not using Count() KEEP
# def clean(self): # this works in model!
    #     self.print_total += 1


# moved to proxies 
        # ???
        # self.xprint_notes = self.product.print_notes
        # self.xcut_notes = self.product.cut_notes
        # self.xpack_notes = self.product.pack_notes

# def test_item_complete(self): # expolration/in progress
    #     cumm = True
    #     for wf in work_field_names:
    #         cumm &= getattr(self, 'complete_'+wf)
    #     if cumm:
    #         self.item_complete = True
    # def tally_complete(self, name): # need to reimpliment on pure form fields
    #     ''' the 'complete' checkbox will be set true if tally >= quantity ; alternativly 
    #         the worker can set the checkbox and this will add missing number to the tally with ',,' marker'''
    #     try:
    #         qty = self.quantity
    #         diff =  qty - getattr(self, name+'_total')
    #         if (diff > 0) and getattr(self, 'complete_'+name):
    #             setattr(self, 'tally_'+name, getattr(self, 'tally_'+name) + ',,' + str(diff))
    #         setattr(self, 'complete_'+name, True if (getattr(self, name+'_total') >= qty) else False)
    #         # if getattr(self, 'complete_'+name):
    #         #     self.test_item_complete()
    #     except:
    #         pass
    # def set_item_complete(self):
    #     for wf in work_field_names:
    #         tally_complete        

     # flag to show commpleted processes for the orderitem 
    #complete_print = models.BooleanField(default=False, verbose_name='complete')
    #complete_cut = models.BooleanField(default=False, verbose_name='complete')
    #complete_weld = models.BooleanField(default=False, verbose_name='complete')
    #complete_stuff = models.BooleanField(default=False, verbose_name='complete')
    #complete_pack = models.BooleanField(default=False, verbose_name='complete')