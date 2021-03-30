from django.db import models
from django.db.models import Q, F, Count, Sum, ExpressionWrapper, DecimalField, IntegerField
#from django.utils.html import format_html
#import datetime
from ..utils import ss, work_field_names, decorate  #, sumtally, get_roll_groups
#from .orderitem import OrderItem
import erp  



class ProductDisplayCategoryManager(models.Manager):
    ''' optimize queries with prefetches and annotations'''
    # modest improvement
    def get_queryset(self):
        qs =  super().get_queryset().prefetch_related(
            'type'
        )
        #qs = qs.select_related('product__type', 'order', 'order__container','order__company')
        #qs = qs.prefetch_related(models.Prefetch(''))
        #qs = qs.annotate(jjj=models.Value(6, output_field=models.IntegerField()),
        #jj2=models.Value(4, output_field=models.IntegerField())) # testing
        #pp={'jj3':models.Value(4, output_field=models.IntegerField())}
        #qs = qs.annotate(**pp)
        #ProductCategories = list(ProductDisplayCategory.objects.values_list('title',flat=True))
        return qs

class ProductDisplayCategory(models.Model):
    objects = ProductDisplayCategoryManager()
    title = models.CharField(max_length=30, blank=True, default='')
    class Meta:
        verbose_name_plural = 'Product Display Categories'
    @property
    def type_count(self):
        return self.type.count()
    #def enumerate(self):
    #    return list(self.objects.values_list('title',flat=True))
    def __str__(self):
        return self.title

class class_ccc():
    try: # requires restart on changes, fixme
        ProductCategories = ProductDisplayCategory.objects.values_list('title',flat=True)
    except:
        # required for new/clean DB startup
        ProductCategories = ['dummy']
    def __call__(self, qq):
        category_remain_process = [] 
        for category in self.ProductCategories:
            category_remain_process.append(qq.format(category=category))
        return category_remain_process

ccc = class_ccc()

"""def ccc(qq):
    ''' example call: ccc('{category}_remain')'''
    try:
        ProductCategories = list(ProductDisplayCategory.objects.values_list('title',flat=True))
    except:
        # required for new/clean DB startup
        ProductCategories = ['dummy']
    '''e.g. arm_remain_print, only used for display colums etc not functions'''
    category_remain_process = [] 
    for category in ProductCategories:
        category_remain_process.append(qq.format(category=category))
    return category_remain_process"""


class ProductTypeManager(models.Manager):
    def get_queryset(self):
        #from .product import ccc
        #categories = ccc('{category}')
        qs = super().get_queryset().prefetch_related(
            #'products',
            #
        ).select_related(
           # 'category',
        )
        return qs

class ProductType(models.Model):
    title = models.CharField(max_length=30, blank=True, default='')
    category = models.ForeignKey('ProductDisplayCategory', related_name='type', on_delete=models.PROTECT, blank=True, null=True)
    # ensure utils.work_field_names is kept upto date with these
    print = models.BooleanField(default=False)
    cut = models.BooleanField(default=False)
    weld = models.BooleanField(default=False)
    stuff = models.BooleanField(default=False)
    pack = models.BooleanField(default=True)
    pcut = models.BooleanField(default=False)
    glue = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    @property
    def workfields_defined(self):
        return [x for x in work_field_names if getattr(self, x)]
    @property
    def workfields_not_defined(self):
        return [x for x in work_field_names if not getattr(self, x)]
    def product_count(self):
        return self.products.count()


class ProductRange(models.Model):
    company = models.ForeignKey('Company', related_name='ranges', on_delete=models.PROTECT)
    title = models.CharField(max_length=120)
    def __str__(self):
        return '%s' % (self.title)



class ProductQuerySet(models.QuerySet):
    def filtered_orders(self):
        return  erp.admin.OrderItem.objects.filter(product__id = self.id).values_list('quantity', flat = True)
    # def in_session(self):
    #     now = timezone.now()
    #     return self.filter(start__lte=now, end__gte=now)

class ProductManager(models.Manager):
    def get_queryset(self):
        #qs = super().get_queryset().prefetch_related(
        qs = ProductQuerySet(self.model, using=self._db).prefetch_related(
            'productnotes',
            #'items',
        ).select_related(
            'type',
            'company',
        )
        return qs
    def filtered_orders(self):
        return self.get_queryset().filtered_orders()


class Product(models.Model):
    objects = ProductManager()
    company = models.ForeignKey('Company', related_name='products', on_delete=models.PROTECT)#, blank=True, null=True)
    type = models.ForeignKey('ProductType', related_name='products', on_delete=models.PROTECT)#, blank=True, null=True)
    title = models.CharField(max_length=120)#.TextField() #
    price = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)
    SKU = models.CharField(max_length=20, blank=True, default='')
    barcode = models.CharField(max_length=20, blank=True, default='')
    #
    overprints = models.SmallIntegerField(blank=True, null=True)
    #
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['company', 'type', 'title'], name='unique_product')
        ]
    def __str__(self):
        return '%s %s' % (self.type.title, self.title)
    def all_notes(self):
        vv = []
        for note in self.productnotes.all():
            vv.append(f'{note.process}: {note.note}')
        return ' | '.join(vv)
    @property
    @decorate(short_description = "Orders/Quantity")
    def sales_count(self):
        #count = erp.admin.OrderItem.objects.aggregate(count=Sum('quantity', filter=Q(product = self)))["count"]
        #count =  erp.admin.OrderItem.objects.filter(product__id = self.id).aggregate(count=Sum(F('quantity'), 
        #output_field=IntegerField()))["count"]
        qs = erp.admin.OrderItem.objects.filter(product_id = self.id).values_list('quantity', flat = True)
        #self.filtered_orders()
        norders = len(qs) #qs.count()
        count = sum(qs) #qs.aggregate(count=Sum(F('quantity'), output_field=IntegerField()))["count"]
        count = count or 0
       
        return f'{norders}/{count}'
    #    return self.products.count()
    
