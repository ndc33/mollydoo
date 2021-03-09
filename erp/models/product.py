from django.db import models
#from django.utils.html import format_html
#import datetime

#from .company import Company
#from .batches import Container
from ..utils import ss, work_field_names, decorate, ProductCategories #, sumtally, get_roll_groups

#ProductCategories = ['CM','ARM','XPVC','M','SPRUNG','OTHER']

class ProductType(models.Model):
    # CATEGORY_CHOICES = (
    #     ('CM',        'CM'),
    #     ('ARM',       'ARM'),
    #     ('XPVC',      'XPVC'),
    #     ('M',         'MATTRESS'),
    #     ('SPRUNG',    'SPRUNG'),
    #     ('OTHER',     'OTHER')
    # )
    CATEGORY_CHOICES = zip(ProductCategories,ProductCategories)

    title = models.CharField(max_length=30, blank=True, default='')
    code = models.CharField(max_length=10, blank=True, default='')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    # ensure utils.work_field_names is kept upto date with these
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


# class SpecNote(models.Model): # not used - in progress
#     ptypes = list(ProductType.objects.values_list('code', flat=True))
#     qqq = ['office', 'delivery', 'all', 'operations'] + work_field_names + ptypes
#     CHOICES = [(j,j) for j in qqq]
#     company = models.ForeignKey('Company', related_name='specnotes', on_delete=models.PROTECT)
#     #type = models.ForeignKey(ProductType, related_name='specnotes', on_delete=models.PROTECT)
#     product = models.ForeignKey('Product', related_name='specnotes', on_delete=models.PROTECT, blank=True, null=True)
#     type = models.CharField(max_length=20, choices=CHOICES)
#     note = models.TextField() 
#     def __str__(self):
#         return '%s: %s' % (self.company.shortname, self.type)



class Product(models.Model):
    company = models.ForeignKey('Company', related_name='products', on_delete=models.PROTECT)#, blank=True, null=True)
    type = models.ForeignKey('ProductType', related_name='products', on_delete=models.PROTECT)#, blank=True, null=True)
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
    #
    overprint = models.SmallIntegerField(blank=True, null=True)
    #
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['company', 'type', 'title'], name='unique_product')
        ]
    def __str__(self):
        return '[%s] %s' % (self.type.code, self.title)
