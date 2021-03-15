
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.db.models import Q, F, Count, Sum

from .orderitem import OrderItem
from .order import Order
from ..utils import decorate, work_field_names_plural
from ..models import SpecNote


class OrderItemTemplate(OrderItem):
    process = None # defined on inheritance below
    class Meta:
        proxy = True
    def __str__(self):
        return '%s of %s' % (self.quantity, self.product)
    @property
    @decorate(short_description = "complete", boolean=True)
    def complete2(self):
        if getattr(self, self.process+'_total') == self.quantity:
            return True
        return False
    def clean(self): # this works for modifying
        tallytotal = getattr(self, self.process + '_tallytotal')
        if 'error' in str(tallytotal):
            setattr(self, self.process+'_total', None) 
            raise ValidationError(tallytotal)
        if isinstance(tallytotal, int):
            if tallytotal > self.quantity:
                raise ValidationError("** Items in Tally Exceed Required Quantity - Please see Printroom if Required to Record Overprints**")
            else:
                setattr(self, self.process + '_total', tallytotal)
    def save(self, *args, **kwargs):
        #self.tally_complete2()
        super().save(*args, **kwargs)
    @property
    def remain(self):
        tmp = getattr(self, self.process + '_remain')
        return format_html('<span style="color: #{};">{}</span>', '787878', tmp)
    def __str__(self):
        # copied from old, check if required
        return '%s of %s' % (self.quantity, self.product) 
    

class OrderItemPrint(OrderItemTemplate):
    process = 'print'
    class Meta:
        proxy = True
    @property
    @decorate(short_description = work_field_names_plural[process])
    def total_html(self):
        return format_html('<b>{}</b>', getattr(self, self.process + '_total')) 

class OrderItemCut(OrderItemTemplate):
    process = 'cut'
    class Meta:
        proxy = True
    @property
    @decorate(short_description = work_field_names_plural[process])
    def total_html(self):
        return format_html('<b>{}</b>', getattr(self, self.process + '_total')) 
   

class OrderItemWeld(OrderItemTemplate):
    process = 'weld'
    class Meta:
        proxy = True
    @property
    @decorate(short_description = work_field_names_plural[process])
    def total_html(self):
        return format_html('<b>{}</b>', getattr(self, self.process + '_total')) 

class OrderItemStuff(OrderItemTemplate):
    process = 'stuff'
    class Meta:
        proxy = True
    @property
    @decorate(short_description = work_field_names_plural[process])
    def total_html(self):
        return format_html('<b>{}</b>', getattr(self, self.process + '_total')) 

class OrderItemPack(OrderItemTemplate):
    process = 'pack'
    class Meta:
        proxy = True
    @property
    @decorate(short_description = work_field_names_plural[process])
    def total_html(self):
        return format_html('<b>{}</b>', getattr(self, self.process + '_total')) 

class OrderItemOps(OrderItem):
    class Meta:
        proxy = True
    @property
    def progress(self):
        #return '{0:.0f}%'.format(self.item_progress) 
        color = '787878'
        # <small>
        return format_html('<span style="color: #{};">{}</span>', color, '{0:.0f}%'.format(self.item_progress))
    def __str__(self):
        return '%s of %s' % (self.quantity, self.product)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)




# --- Order ----------

class OrderTemplate(Order):
    process = None # defined on inheritance below



class OrderOps(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Operations Order View'
    def __str__(self): # added only for experimenting with adding totals-row to list-view)
        if self.id:
            return '%s'% self.id
        else:
            return self.custom_alias_name
   
  

class OrderPrint(Order):
    process = 'print'
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Print View'
    


class OrderCut(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Cut View'


class OrderWeld(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Weld View'


class OrderStuff(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Stuff View'

class OrderPack(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Pack View'