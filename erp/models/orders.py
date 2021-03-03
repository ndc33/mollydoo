from django.db import models
from django.utils.html import format_html
import datetime

from .company import Company
from .batches import Container
from ..utils import ss, work_field_names, decorate, sumtally

#from simple_history.models import HistoricalRecords
#from smart_selects.db_fields import ChainedForeignKey


# https://django-model-utils.readthedocs.io/en/latest/managers.html
#from model_utils.managers import InheritanceManager, QueryManager

#

class ProductType(models.Model):
    title = models.CharField(max_length=30, blank=True, default='')
    code = models.CharField(max_length=10, blank=True, default='')
    print = models.BooleanField(default=False)
    cut = models.BooleanField(default=False)
    weld = models.BooleanField(default=False)
    stuff = models.BooleanField(default=False)
    pack = models.BooleanField(default=True)
    def __str__(self):
        return self.title
    @property
    def workfields_defined(self):
        return [x for x in work_field_names if getattr(self, x)]
    @property
    def workfields_not_defined(self):
        return [x for x in work_field_names if not getattr(self, x)]


class SpecNote(models.Model): # not used - in progress
    ptypes = list(ProductType.objects.values_list('code', flat=True))
    qqq = ['office', 'delivery', 'all', 'operations'] + work_field_names + ptypes
    CHOICES = [(j,j) for j in qqq]
    company = models.ForeignKey('Company', related_name='specnotes', on_delete=models.PROTECT)
    #type = models.ForeignKey(ProductType, related_name='specnotes', on_delete=models.PROTECT)
    product = models.ForeignKey('Product', related_name='specnotes', on_delete=models.PROTECT, blank=True, null=True)
    type = models.CharField(max_length=20, choices=CHOICES)
    note = models.TextField() 
    def __str__(self):
        return '%s: %s' % (self.company.shortname, self.type)



class Product(models.Model):
    company = models.ForeignKey(Company, related_name='product', on_delete=models.PROTECT)#, blank=True, null=True)
    type = models.ForeignKey('ProductType', related_name='product', on_delete=models.PROTECT)#, blank=True, null=True)
    title = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.TextField(blank=True, default='')
    # new
    print_notes = models.TextField(blank=True, default='')
    cut_notes = models.TextField(blank=True, default='')
    pack_notes = models.TextField(blank=True, default='')
    #
    active = models.BooleanField(default=True)
    SKU = models.CharField(max_length=20, blank=True, default='')
    barcode = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['company', 'type', 'title'], name='unique_product')
        ]
    def __str__(self):
        return '[%s] %s' % (self.type.code, self.title)


class Order(models.Model):
    # verbose_name='Order ID'
    sentinal_text = "---press update to copy STD notes---"
    id = models.AutoField(primary_key=True, verbose_name="Order") # get verbose name on ID - not required
    company = models.ForeignKey(Company, related_name='order', on_delete=models.PROTECT)
    container = models.ForeignKey(Container, related_name='order', default=1, on_delete=models.PROTECT)
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
    #xx = models.BooleanField()#null=True)
    class Meta:
        ordering = ('LD',)
    def save(self, *args, **kwargs):
        try:
            companyid = self.company_id
            if self.xorder_notes == self.sentinal_text:
                self.xorder_notes = Company.objects.get(id=companyid).order_notes
            if self.xmanufacture_notes == self.sentinal_text:
                self.xmanufacture_notes = Company.objects.get(id=companyid).manufacture_notes
            if self.xdelivery_notes == self.sentinal_text:
                self.xdelivery_notes = Company.objects.get(id=companyid).delivery_notes
            if not self.id:
                self.OD = datetime.date.today()
        except:
            pass
        super().save(*args, **kwargs)
    def __str__(self):
        return '%s %s' % (self.company.shortname, self.id)

    @property 
    def batch(self):
        return self.batchorder.batch
    @property
    @decorate(admin_order_field='batchorder__batch__title')
    def batch_name(self):
        return self.batchorder.batch.title
    @property
    @decorate(admin_order_field='batchorder__batch__DD')
    def batch_info(self):
        temp = None
        try:
            title = self.batchorder.batch.title
            DD = self.batchorder.batch.DD
            if DD:
                DD=DD.strftime("%a %d %b")
            temp = '%s - %s' % (title, DD)
        except:
            pass
        return temp
    @property
    @decorate(admin_order_field='batchorder__batch__DD')
    def DD(self):
        dd = None
        try:
            dd = self.batchorder.batch.DD
            if dd:
                dd = dd.strftime("%a %d %b")
        except:
            pass
        return dd
    # @property
    # @decorate(admin_order_field='batchorder__batch__MD')
    # def MD(self):
    #     dd = None
    #     try:
    #         dd = self.batchorder.batch.MD
    #         if dd:
    #             dd = dd.strftime("%a %d %b")
    #     except:
    #         pass
    #     return dd
    @property
    #@decorate(admin_order_field='status') # is required to return query
    def status(self):
        # just a crude mock-up for future functionality
        # note: need lots of data checking on inputs for incoherent combinations 
        status = 'Shelf' # means unassigned
        if a := getattr(self, 'batchorder', None):
            if a.batch.DD:
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
    def LD_markup(self): # need to differentiate this with undeline or such
        color = '8c8c8c' if not self.LD_S else '000000'
        return format_html(
            '<span style="color: #{};">{}</span>',
            color,
            self.LD,
        )
    @property
    @decorate(short_description = "CD")
    def CD_markup(self):
        color = '8c8c8c' if not self.CD_C else '000000'
        return format_html(
            '<span style="color: #{};">{}</span>',
            color,
            self.CD,
        )
    def tCM(self):
        import ipdb; ipdb.set_trace()
        return 1


# class OrderItemManager(models.Manager):
#     def workfields(self):
#         return 0


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='item', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='item', on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(default=1)
    # x_ means copied over on creation
    xprice = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    xnotes = models.TextField(blank=True, default='')
    xprint_notes = models.TextField(blank=True, default='', help_text='xPrint Notes')
    xcut_notes = models.TextField(blank=True, default='')
    xpack_notes = models.TextField(blank=True, default='')
    # not used
    print = models.PositiveSmallIntegerField(default=0)
    cut = models.PositiveSmallIntegerField(default=0)
    weld = models.PositiveSmallIntegerField(default=0)
    stuff = models.PositiveSmallIntegerField(default=0)
    pack = models.PositiveSmallIntegerField(default=0)
    # to be removed, will use unbound formfield with logic
    printed =  models.BooleanField(default=False, verbose_name='complete')
    cutx =  models.BooleanField(default=False, verbose_name='complete')
    welded =  models.BooleanField(default=False)
    stuffed =  models.BooleanField(default=False)
    packed =  models.BooleanField(default=False)
    # new
    tally_print = models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_cut = models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_weld = models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_stuff = models.CharField(max_length=120, blank=True, default='', verbose_name='tally')
    tally_pack = models.CharField(max_length=120, blank=True, default='', verbose_name='tally')

    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['order', 'product'], name='unique_order_item')
        ]
    def __str__(self):
        return '%s' % self.id
    # methods below that call another models calculated-properties inherit ordering and except protection
    @property
    def company(self):
        return self.order.company
    @property
    def order_notes(self):
        return '%s' % (self.order.notes)
    @property
    def products_allowed(self):
        return self.order.products
    @property
    def work_fields(self):
        return self.product.type.workfields_defined
    # @property
    # def batchid(self):
    #     return self.order.batchid
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
    # @property
    # def MD(self):
    #     return self.order.MD
    @property
    @decorate(admin_order_field='order__id')
    def norder(self):
        try:
            dd = self.order.id 
        except:
            dd = None
        return dd
    @property
    @decorate(short_description = "Total")
    def print_total(self):
        return sumtally(self.tally_print)
    @property
    @decorate(short_description = "Total")
    def cut_total(self):
        return sumtally(self.tally_cut)
    # @property
    # def product_notes(self):
    #     return self.product.notes
    def save(self, *args, **kwargs):
        if not self.id: # suprised it works-> alternative go through form clean
            self.xprice = self.product.price
            self.xnotes = self.product.notes
        else:
            qty = self.quantity
            self.printed = True if (self.print_total > qty) else False
            self.cutx = True if (self.cut_total > qty) else False
        #import ipdb; ipdb.set_trace() 
            # self.xprint_notes = self.product.print_notes
            # self.xcut_notes = self.product.cut_notes
            # self.xpack_notes = self.product.pack_notes
        super().save(*args, **kwargs)


# ---------------------------

#dd = BatchOrder.objects.get(order__id=self.id).batch.dispatch_date # KEEP as query example
# my_property.fget.short_description = u'Property X' #for info

# to do from model properties https://marioorlandi.medium.com/how-to-annotate-a-django-queryset-with-calculated-properties-and-use-them-in-modeladmin-for-e21dc41ac27f

# class DeManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().annotate(
#             s_d=Case(
#                 When(fr=True, then='s_d'),
#                 When(fr=False, then=F('gd') + F('na')),
#                 default=Value(0),
#                 output_field=IntegerField(),
#             )
#         )


    # https://django-smart-selects.readthedocs.io/en/latest/usage.html
    # product = ChainedForeignKey(
    #     Product,
    #     chained_field="order",
    #     chained_model_field="company",
    #     show_all=False,
    #     auto_choose=False,
    #     sort=False, 
    #     related_name='item', 
    #     on_delete=models.PROTECT)