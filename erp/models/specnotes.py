from django.db import models
from ..utils import work_field_names


class SpecNote(models.Model): # not used - in progress
    #ptypes = list(ProductType.objects.values_list('title', flat=True))
    qqq = ['office', 'delivery', 'all', 'operations'] + work_field_names #+ ptypes
    process_choices = zip(work_field_names, work_field_names)
    CHOICES = [(j,j) for j in qqq]
    company = models.ForeignKey('Company', related_name='specnotes', on_delete=models.PROTECT, blank=True, null=True)
    type = models.ForeignKey('ProductType', related_name='specnotes', on_delete=models.PROTECT, blank=True, null=True)
    product = models.ForeignKey('Product', related_name='specnotes', on_delete=models.PROTECT, blank=True, null=True)
    order = models.ForeignKey('Order', related_name='specnotes', on_delete=models.PROTECT, blank=True, null=True)
    process = models.CharField(max_length=20,choices=process_choices,blank=True, null=True)
    choice = models.CharField(max_length=20,choices=CHOICES,blank=True, null=True)
    note = models.TextField() 
    def __str__(self):
        return '%s %s %s %s %s' % (
        getattr(self.company, 'shortname',''), 
        self.type or '', 
        self.product or '',
        self.order or '',
        self.process or '',
        )


class OrderNotesManager(models.Manager):
    def create_ordernotes(self, title):
        book = self.create(title=title)
        # do something with the book
        return book
        
class OrderNotes(models.Model):
    order = models.ForeignKey('Order', related_name='notebag', on_delete=models.PROTECT, blank=True, null=True)
    pass

"""
logic 
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