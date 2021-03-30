from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import datetime

from ..utils import ss, decorate, shortdate
from .order import Order 


class Batch(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    dispatch_date = models.DateField(auto_now_add=False, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name_plural = 'Batches'
    @property
    def orders_list(self):
        qq = self.orders.values_list(flat=True)
        return list(qq) or '' 
    def searchdate(self):
        return self.__str__
    def __str__(self):
        # problem with showing markup in autocomplete_fields
        #return  format_html('<span style="color: #{};">{}</span>', '8c8c8c', self.title)
        return mark_safe('%s %s' % (self.title, shortdate(self.dispatch_date) or ''))

