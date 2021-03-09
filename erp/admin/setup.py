from django import forms
from django.db import models
#from django.db.models import Q, F, Count
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

#from simple_history.admin import SimpleHistoryAdmin
#from import_export import resources
#from import_export.admin import ImportExportModelAdmin, ImportExportMixin
#from django.apps import apps
#ModelName = apps.get_model('app_name', 'ModelName')

#from erp import models as xmodels
#from ..models import Dummy

from ..utils import ss, setwidget

# prefetch notes
# https://hansonkd.medium.com/performance-problems-in-the-django-orm-1f62b3d04785
# https://stackoverflow.com/questions/51212021/django-prefetch-related-prefetch-nested
# https://stackoverflow.com/questions/27116770/prefetch-related-for-multiple-levels

def text_box(rows, cols):
    #https://stackoverflow.com/questions/18738486/control-the-size-textarea-widget-look-in-django-admin
    text_box = {  
            models.TextField: {'widget': forms.Textarea(
                            attrs={'rows': rows, 'cols': cols,})},#'style': 'height: 1em;'
        }
    return text_box

class ERP(admin.AdminSite):
    site_header = 'MollyDoo ERP'
    site_title = 'MollyDoo ERP'
    index_title = 'ERP'
    site_url = ''
    enable_nav_sidebar = False
    
erp_admin = ERP(name='erp')
site_proxy = erp_admin
name_proxy = 'erp' #'admin'

class admin2(admin.ModelAdmin): # SimpleHistoryAdmin 
    # NOTE the 5 vars here used as directives, they are used throught 
    remove_pk_controls = []
    listviewtitle = None
    suppress_form_controls = {}
    producttitle = False
    ordertitle = False
    modify_labels = {}
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs) 
        for pkn in self.remove_pk_controls:
            # get rid of annoying add/change etc icons next to primary key
            if w:= form.base_fields.get(pkn):
                setwidget(w.widget)
            # if pkn == 'company':
            #     widget.attrs['readonly'] = True 
        for key,value in self.modify_labels.items():
            # overwrite labels
            form.base_fields[key].label = value 
        for field in form.base_fields: # keep for info
            # Note from docs: the label suffix is added only if the last character of the label isn’t a punctuation character
            if form.base_fields.get(field).required:
                form.base_fields.get(field).label_suffix = ' *:' # for play/example only
            #import pdb; pdb.set_trace()
        return form
    def xs1(self, obj):
        # used for spacing before using .css changes 
        return ''
    xs3 = xs2 = xs1
    xs1.short_description = '' 
    def changelist_view(self, request, extra_context=None):
        if self.listviewtitle: # todo finish
            color = '000000'#'787878'
            qq = format_html(
                #('{} <span style="color: #{};">&nbsp<sub>{}</sub></span>'
            '<span style="color: #{};">{}</span>',
            color,
            self.listviewtitle,
            )
            extra_context = {'title': qq}#self.listviewtitle}
        return super().changelist_view(request, extra_context=extra_context)
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if (self.producttitle): # override title (since obj required)
            self.suppress_form_controls['title'] = '%s of %s' % (obj.quantity, obj.product)
        if (self.ordertitle): # override title (since obj required)
            try: 
                batch_title = obj.batchorder.batch.title
            except:
                batch_title = None
            # ugly botch to fit with current architecture
            self.suppress_form_controls['title'] = mark_safe(
                '%s%s Order: %s%s Batch: %s' % 
                (obj.company.name, ss*18, obj.id, ss*36, obj.batch_info)
                )
        context.update({**self.suppress_form_controls})
        return super().render_change_form(request, context, add, change, form_url, obj)



# --------- ignore below -------------

# further examples of formfield_overrides
#models.IntegerField: {'widget': widgets.NumberInput(attrs={'size':'5'})},
#models.TextField: {'widget': widgets.Textarea(attrs={'rows':4, 'cols':40})},
#models.CharField: {'widget': widgets.TextInput(attrs={'size': '10'})}

# from functools import wraps
"""
class AddressResource(resources.ModelResource): #import-export
    class Meta:
        model = Address
        #exclude = ('created_at','modified') # check required or desirable
        skip_unchanged = True
        report_skipped = False
"""
# class AddAdmin(ImportExportModelAdmin):
#     resource_class = AddressResource

# erp_admin.register(Address, AddAdmin)

# def create_modeladmin(modeladmin, model, name = None):
#     class  Meta:
#         proxy = True
#         app_label = model._meta.app_label

#     attrs = {'__module__': '', 'Meta': Meta}

#     newmodel = type(name, (model,), attrs)

#     admin.site.register(newmodel, modeladmin)
#     return modeladmin

# class MyDummyAdmin(DummyAdmin):
#     def get_queryset(self, request):
#         return self.model.objects.filter(user = request.user)

# create_modeladmin(MyDummyAdmin, name='my-dummy', model=Dummy)
# create_modeladmin(DummyAdmin, name='dummy', model=Dummy)

#@admin.register(Dummy, site=admin.sites.site)
# class DummyAdmin(admin.ModelAdmin):
#     # for example note
#     def changelist_view(self, request, extra_context=None):
#         # Add extra context data to pass to change list template
#         extra_context = extra_context or {}
#         extra_context['my_store_data'] = {'onsale':['Item 1','Item 2']}
#         # Execute default logic from parent class changelist_view()
#         return super().changelist_view(
#             request, extra_context=extra_context
#         ) # could insert via html via read_only list_item but no point?
#     pass
    
# class MyDummy(models.Dummy):
#     class Meta:
#         proxy = True

# #@admin.register(MyDummy, site=admin.sites.site)
# class MyDummyAdmin(DummyAdmin):
#     pass
