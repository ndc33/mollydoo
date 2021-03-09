
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from .orderitem import OrderItem
from .order import Order
from ..utils import decorate

# query optimisations for each process?

class OrderItemPrint(OrderItem):
    process = 'print'
    class Meta:
        proxy = True
    def __str__(self):
        return '%s of %s' % (self.quantity, self.product)
    @decorate(short_description = "complete", boolean=True)
    def complete2(self):
        if getattr(self,self.process+'_total') == self.quantity:
            return True
        return False
    def clean(self): # this works for modifying
        tallytotal = getattr(self, self.process + '_tallytotal')
        if 'error' in str(tallytotal):
            setattr(self,self.process+'_total', None) 
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
        color = '787878'
        return format_html(
            '<span style="color: #{};">{}</span>',
            color,
            tmp,
        )
        #return getattr(self, self.process + '_remain')
    @property
    @decorate(short_description = "quantity")
    def Bquantity(self):
        return format_html('<b>{}</b>', super().quantity)
        #return getattr(self, self.process + '_remain')
    def __str__(self):
        # copied from old, check if required
        return '%s of %s' % (self.quantity, self.product) 
    


class OrderItemCut(OrderItemPrint):
    process = 'cut'
    class Meta:
        proxy = True

class OrderItemWeld(OrderItemPrint):
    process = 'weld'
    class Meta:
        proxy = True

class OrderItemStuff(OrderItemPrint):
    process = 'stuff'
    class Meta:
        proxy = True

class OrderItemPack(OrderItemPrint):
    process = 'pack'
    class Meta:
        proxy = True

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

class OrderOps(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Operations View'
    def __str__(self): # added only for experimenting with adding totals row to list view)
        if self.id:
            return '%s'% self.id
        else:
            return self.custom_alias_name
  


class OrderPrint(Order):
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