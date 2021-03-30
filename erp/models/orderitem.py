from django.db import models
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django.db.models import Q, F, Count, Value, When, Case, Sum, ExpressionWrapper, DecimalField 
from django.db.models.functions import Greatest, Least
import datetime
from decimal import Decimal
from .company import Company
#from .batches import Container
from ..utils import ss, work_field_names, decorate, sumtally, get_roll_groups

import operator
from functools import reduce


""" # explore idea for ui defined processes
class process(models.Model):
    title = models.CharField(max_length=30, blank=True, default='')
    item = models.ForeignKey('OrderItem', related_name='process', on_delete=models.PROTECT)
    tally =   models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    total =   models.PositiveSmallIntegerField(default=0, verbose_name='printed')
    def remain(self):
        return self.item quantity - self.total
    def progress(self):
        return self.total/self.item quantity
    
"""




class OrderItemRelatedModelMethods():
    @property
    def print_locations(self):
        # only used by processes downstream of print
        roll_data = get_roll_groups(self.tally_print)
        return roll_data[1] 
    @property
    def products_allowed(self):
        return self.order.products # self.order.company.own_products 
    @property
    def work_fields(self):
        return self.product.type.workfields_defined
    @property
    def overprints(self):
        '''only called by works-print-view'''
        return self.product.overprints or ''

# -----

# class OrderItemQuerySet(models.QuerySet):
#     def filtered_orders(self):
#         return  self.filter(product__id = self.id).values_list('quantity', flat = True)
#     # def in_session(self):
#     #     now = timezone.now()
#     #     return self.filter(start__lte=now, end__gte=now)


class OrderItemManager(models.Manager):
    #use_for_related_fields = True
    ''' optimize queries with prefetches and annotations'''
    # modest improvement
    def get_queryset(self):
        default = Value('-')
        output_field=models.CharField()  
 #**{f'{process}_remain2': case for process in work_field_names}
        process_total_exp = reduce(operator.add, (Least(F(f'{process}_total'), F('quantity')) for process in work_field_names))
        process_count_exp = reduce(operator.add, (F(f'product__type__{process}') for process in work_field_names))
        qs = super().get_queryset().prefetch_related(
            #
            ).select_related(
            'product__type', 
            'product',
            'product__type__category', # very good
            'order', 
            'order__batch', # speeds up item listing
            'order__company'  # speeds up item listing
            ).annotate(
                process_total = process_total_exp
            ).annotate(
                process_count = ExpressionWrapper(process_count_exp, output_field=models.IntegerField())
            ).annotate(
                **{f'{process}_remain2': Case(
                When(Q(**{f'product__type__{process}':True}), then=Greatest(F('quantity')-F(f'{process}_total'),Value(0))),
                default=default, 
                output_field=output_field) for process in work_field_names}
              #old  **{f'{process}_remain2':ExpressionWrapper((F('quantity')-F(f'{process}_total'))*F(f'product__type__{process}'),output_field=models.IntegerField())
              #      for process in work_field_names}
            ).annotate(
                progress2=ExpressionWrapper(F('process_total') * Decimal('100.0')/F('process_count')/F('quantity'), 
                    output_field=models.DecimalField(0))# FloatField())
            ).annotate(
                #cannot see in the order annotation, but can see on general queries
                #category = ExpressionWrapper(F('product__type__category__title'), output_field=models.CharField())
            )
        html = format_html('<span style="color: #{};">{}</span>', '008000', 'ggg item green')
        qs = qs.annotate(ggg = models.Value(html, output_field=models.TextField())) # testing
        return qs



class OrderItem( 
    OrderItemRelatedModelMethods, 
    #OrderItemTotalSummaryMethods, 
    #OrderItemRemaingMethods,
    models.Model
    ):
    #
    objects = OrderItemManager()
    order =     models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE)
    product =   models.ForeignKey('Product', related_name='items', on_delete=models.PROTECT)
    quantity =  models.PositiveSmallIntegerField(default=1)
    # x_ means copied over on creation
    xprice =        models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    # text field to hold the process tallies e.g. '3,7,23' parsed/summed into to <process>_total methods above
    tally_print =   models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_cut =     models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_weld =    models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_stuff =   models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_pack =   models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_pcut =    models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_glue =    models.CharField(max_length=120, blank=True, default='', verbose_name='tally')

    #
    print_total =   models.PositiveSmallIntegerField(default=0, verbose_name='printed')#blank=True, null=True)
    cut_total =     models.PositiveSmallIntegerField(default=0, verbose_name='cut')#blank=True, null=True)
    weld_total =    models.PositiveSmallIntegerField(default=0, verbose_name='welded')#blank=True, null=True)
    stuff_total =   models.PositiveSmallIntegerField(default=0, verbose_name='stuffed')#blank=True, null=True)
    pack_total =    models.PositiveSmallIntegerField(default=0, verbose_name='packed')#blank=True, null=True)
    pcut_total =    models.PositiveSmallIntegerField(default=0, verbose_name='pvc_cut')#blank=True, null=True)
    glue_total =    models.PositiveSmallIntegerField(default=0, verbose_name='glued')#blank=True, null=True)
    #
    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['order', 'product'], name='unique_order_item')
        ]
        #base_manager_name = 'objects'#'OrderItemManager'
    def __str__(self):
        if self.id:
            return '%s' % self.id
        else:
            return 'total'
    @property
    @decorate(short_description = "quantity")
    def quantity_html(self):
        return format_html('<b>{}</b>', self.quantity)
    def save(self, *args, **kwargs):
        #import pdb; pdb.set_trace() 
        if self._state.adding is True:  #if not self.id: 
            # pre form-filling wont work if we do not have FK already saved
            # this is safe from cross-user-saving since only triggered on creation 
           # try:
            self.xprice = self.product.price
            #except:
            #    pass
        super().save(*args, **kwargs)
    @property # 20/03
    def progress(self):
        # <small>
        return format_html('<span style="color: #{};">{}</span>', '787878', '{0:.0f}%'.format(self.progress2)) #self.item_progress
    def all_notes(self):
        vv = []
        for note in self.product.productnotes.all():
            vv.append(f'{note.process}: {note.note}')  # inline concatonated text
        return ' | '.join(vv) or '-'
    # testing only
    # def _ppp(self): # test of qs annotations
    #     return self.ppp
    # def myfunc2(self, arg):
    #     return arg
    
    
    
   
    


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

