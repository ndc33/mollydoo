from django.db import models
#from django.core.exceptions import ValidationError
#from django.utils.html import format_html
#from django.db.models import Q, F, Count, Sum

from .orderitem import OrderItem
#from .order import Order
from ..utils import decorate, sumtally, get_roll_groups #work_field_names_plural,
#from ..models import SpecNote, ProductDisplayCategory, ccc


class OrderItemProxy(OrderItem):
    #process = defined on inheritance/generation
    class Meta:
        proxy = True
        #managed=False
    def func_tally(self, process):
        if not getattr(self.product.type, process):
            return '-'
        if process == 'print':
            # unique to print (to track locations of print)
            roll_data = get_roll_groups(self.tally_print)
            return roll_data[0] # todo find a way to display roll totals 
        else:
            return sumtally(getattr(self, f'tally_{process}'))
    def clean(self):
        process = self.process # attaced by botch *******
        
        if process == 'all':
            pass
        else:
            #tallytotal = getattr(self, f'{process}_tallytotal') # old individual methods
            tallytotal = self.func_tally(process)
            if 'error' in str(tallytotal):
                import pdb; pdb.set_trace()
                setattr(self, f'{process}_total', None) 
                raise ValidationError(tallytotal)
            if isinstance(tallytotal, int):
                # this check now disabled
                #if tallytotal > self.quantity:
                 #   pass #raise ValidationError("** Items in Tally Exceed Required Quantity - Please see Printroom if Required to Record Overprints**")
                #else:
                setattr(self, f'{process}_total', tallytotal)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    def __str__(self):
        # copied from old, check if required
        return '%s of %s' % (self.quantity, self.product) 
    
