from django.db import models
from django.utils.html import format_html
from ..utils import work_field_names, decorate


class SpecNote(models.Model): # not used - in progress
    #ptypes = list(ProductType.objects.values_list('title', flat=True))
    qqq = ['office', 'delivery', 'all', 'operations'] + work_field_names #+ ptypes
    process_choices = zip(work_field_names, work_field_names)
    CHOICES = [(j,j) for j in qqq]
    company = models.ForeignKey('Company', related_name='specnotes', on_delete=models.PROTECT)
    type = models.ForeignKey('ProductType', related_name='specnotes', on_delete=models.PROTECT, blank=True, null=True)
    product = models.ForeignKey('Product', related_name='specnotes', on_delete=models.PROTECT, blank=True, null=True)
    #order = models.ForeignKey('Order', related_name='specnotes', on_delete=models.PROTECT, blank=True, null=True)
    process = models.CharField(max_length=20,choices=process_choices,blank=True, null=True)
    choice = models.CharField(max_length=20,choices=CHOICES,blank=True, null=True)
    note = models.TextField() 
    def __str__(self): # to kill
        return '%s %s %s %s' % (
        getattr(self.company, 'shortname',''), 
        self.type or '', 
        self.product or '',
        self.process or '',
        )


class OrderNotesManager(models.Manager):
    def create_ordernotes(self, order):
        ordernotes = self.create(order=order)
        # do something 
        return ordernotes

class OrderNotes(models.Model):
    order = models.ForeignKey('Order', related_name='notebag', on_delete=models.PROTECT, blank=True, null=True)
    pass

"""
logic for universal notes -> not implimented
[c,t,p,o,r]
class 1: are placed on orders, company (or order number?) required
[c,-,-,-,-] -> e.g.specific company, all orders, all processes
[c,-,-,o,r] -> e.g.specific company, specific order, specific process
class 2 are placed on products, company required
[c,t,-,-,-] -> e.g.specific company, specific producttype, all orders, all processes
[c,-,p,-,r] -> specific product, specific process
class 1: [c,o,r] ; class 2 [c,t,p,r]
or to simplify we check the order for type, product and put all notes at the top
-> maybe being able to have a temporary 'global' message e.g. all CM could be usefull?
e.g. new packaging regs for all mattresses in Pack?
(todo remove null on company?)

"""

#process_codes = enumerate(work_field_names+['all'])

#from softdelete.models import SoftDeleteObject #also need SoftDeleteManager

class ProductNote(models.Model):
#class ProductNote(SoftDeleteObject):
    '''attached to product model and copied verbatim to order items as concatonated strings'''
    process_names = work_field_names +['all']
    process_choices = zip(process_names, process_names)
    product = models.ForeignKey('Product', related_name='productnotes', on_delete=models.PROTECT)
    #order = models.ForeignKey('Order', related_name='specnotes', on_delete=models.PROTECT, blank=True, null=True)
    process = models.CharField(max_length=20, choices=process_choices) #,default='all')#, blank=True, null=True)#max_length=20,
    note = models.CharField(max_length=120)#TextField() 
    def __str__(self):
        return 'Note: %s %s' % (self.product, self.process or '')

class OrderNoteAbstract(models.Model): # in progress
    class Meta:
        abstract = True
    process_names = work_field_names +['all']
    process_choices = zip(process_names, process_names)
    #
    process = models.CharField(max_length=20, choices=process_choices) #,default='all')#, blank=True, null=True)#max_length=20,
    note = models.TextField() 
    highlight = models.BooleanField(default=False) 
    def __str__(self):
        return 'Note: %s %s' % (self.company, self.process or '')


class OrderNote(OrderNoteAbstract):
    company = models.ForeignKey('Company', related_name='ordernotes', on_delete=models.CASCADE)
    def __str__(self):
        return 'Note: %s %s' % (self.company, self.process or '')
    def note_html(self):
        style = 'color:red;font-weight:bold' if self.highlight else ''
        #color = '8b0000' if self.highlight else '000000'
        return  format_html('<span style="{};">{}</span>', style, self.note)



class OrderNoteItem(OrderNoteAbstract):
    order = models.ForeignKey('Order', related_name='ordernoteitems', on_delete=models.CASCADE)
    def __str__(self):
        return 'Note: %s %s' % (self.order, self.process or '')
    @property
    @decorate(short_description = "note")
    def note_html(self):
        style = 'color:red;font-weight:bold' if self.highlight else ''
        #color = '8b0000' if self.highlight else '000000'
        return  format_html('<span style="{};">{}</span>', style, self.note)

