from django.db import models
from django.utils.html import format_html
import datetime

from ..utils import ss, decorate

class BatchManager(models.Manager):
    ''' optimize queries with prfetches and annotations'''
    def get_queryset(self):
        qs =  super().get_queryset()
        #qs = qs.prefetch_related('batchorders')
        #qs = qs.select_related('order__company')
        #qs = qs.select_related('batch')
        return qs

class Batch(models.Model):
    objects = BatchManager()
    title = models.CharField(max_length=20, blank=True, default='')
    DD = models.DateField(auto_now_add=False, blank=True, null=True)
    #MD = models.DateField(auto_now_add=False, blank=True, null=True)#, help_text="Manufacturing Date")#, verbose_name="Manufacturing Date")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'Batches'
        ordering = ("-DD",) # just testing
    # @property
    # def orders(self):
    #     return Order.batchorders.objects.filter(order__id=self.id)
    # @property
    # def num_orders(self):
    #     return self.batchorders.count()
    def __str__(self):
        return '%s %s' % (self.id, self.title)


class BatchOrderManager(models.Manager):
    ''' optimize queries with prfetches and annotations'''
    def get_queryset(self):
        qs =  super().get_queryset()
        #qs = qs.select_related('order')
        qs = qs.select_related('order__company')
        #qs = qs.select_related('batch')
        return qs


class BatchOrder(models.Model):
    objects = BatchOrderManager()
    batch = models.ForeignKey(Batch, related_name='batchorders', on_delete=models.CASCADE)
    order = models.OneToOneField('Order', related_name='batchorders', on_delete=models.PROTECT)#,  null=True)
    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['batch', 'order'], name = 'unique_batch_order')
        ]
    @property
    def csn(self):
        try:
            dd = self.order.company.shortname
        except:
            dd = None
        return dd
    @property
    def company(self):
        try:
            dd = self.order.company.name
        except:
            dd = None
        return dd
    def CD(self):
        try:
            dd = self.order.CD
        except:
            dd = None
        return dd
    #@property
    @decorate(short_description = "CD")
    def CD_markup(self):
        return self.order.CD_markup
    #@property
    @decorate(boolean=True) # not working when delared as property
    def CD_C(self):
        try:
            dd = self.order.CD_C
        except:
            dd = None
        return dd
    #CD_C.boolean = True
    #CD_C = property(CD_C)
    def LD(self):
        try:
            dd = self.order.LD
        except:
            dd = None
        return dd
    def __str__(self):
        return '%s' % self.id


class Container(models.Model): # exploration
    title = models.CharField(max_length=255, blank=True, null=True)
    dispatch_date = models.DateField(auto_now_add=False, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
         return '%s %s' % (self.title, self.dispatch_date or '')

# -----old--------

# ARCHIVED
# class PriceList(models.Model):
#     name = models.CharField(max_length=255, blank=True, null=True)
#     company = models.ForeignKey(Company, related_name='pricelist', on_delete=models.CASCADE)
#     #product = models.ForeignKey(Product, related_name='pricelist', on_delete=models.DO_NOTHING)
#     #price = models.DecimalField(max_digits=8, decimal_places=2)

#     def __str__(self):
#         return '%s %s' % (self.company, self.name)

# class PriceListItem(models.Model):
#     pricelist = models.ForeignKey(PriceList, related_name='pricelistitem', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, related_name='pricelist', on_delete=models.DO_NOTHING)
#     price = models.DecimalField(max_digits=8, decimal_places=2)