#from django import forms
#from django.db import models
#from django.db.models import Q, F, Count
from django.contrib import admin
#from django.urls import reverse
#from django.utils.html import format_html
#from django.utils.safestring import mark_safe
#from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

from .setup import erp_admin, site_proxy, name_proxy

from ..models import Order#, OrderItem 
from .workstemplate import WorksTemplateInline, WorksOrderTemplate

# Notes
# individual views per process, queryset filtered on process <'print', 'cut', 'weld', 'stuff', 'pack'>
#   methodology of generating these views may change
# could do with some jquery magic to allow submission on pressing return, 
#   also keep scroll position (default is return to top)

# ------print------

class WorkPrintInline(WorksTemplateInline):
    tally = 'tally_print'
    fields = ('xproduct', 'quantity', 'xnotes', tally, 'total', 'printed')
    process_lookup = 'product__type__print'
    verbose_name_plural = 'Print View'

class WorkPrintView(Order):
    
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Print View'

@admin.register(WorkPrintView, site=site_proxy)
class MPrintOrderAdmin(WorksOrderTemplate):
    inlines = [WorkPrintInline]
    #process_lookup = 'product__type__print'

#-----cut-------

class WorkCutInline(WorksTemplateInline):
    tally = 'tally_cut'
    fields = ('xproduct', 'quantity', 'xnotes', tally, 'total', 'cutx')
    process_lookup = 'product__type__cut'
    verbose_name_plural = 'Cut View'

class WorkCutView(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Cut View'

@admin.register(WorkCutView, site=site_proxy)
class WorksCutOrderAdmin(WorksOrderTemplate):
    inlines = [WorkCutInline]
    #process_lookup = 'product__type__cut'