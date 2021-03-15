#------------inherited by works views-----------------

from django import forms
#from django.db import models
#from django.db.models import Q, F, Count
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
#from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

from .setup import erp_admin, site_proxy, name_proxy
from .setup import text_box
from .setup import container_link

from ..utils import  ss, setwidget

from totalsum.admin import TotalsumAdmin

# likely much cleaner/simpler ways of obtaing the following functionilty
    
class TemplateFilter(admin.SimpleListFilter): # needs further work
    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        types = qs.values_list(self._lookup,self._lookup )
        return list(types.order_by(self._lookup).distinct())
    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(**{self._lookup : self.value()}) # note the trick


class admin2(TotalsumAdmin):#admin.ModelAdmin): # SimpleHistoryAdmin 
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
                batch_title = obj.container__title
            except:
                batch_title = None
            # ugly botch to fit with current architecture
            self.suppress_form_controls['title'] = mark_safe(
                '%s%s Order: %s%s Batch: %s' % 
                (obj.company.name, ss*18, obj.id, ss*36, obj.container)
                )
        context.update({**self.suppress_form_controls})
        return super().render_change_form(request, context, add, change, form_url, obj)




class WorksOrderTemplate(admin2):
    #id_obj = None # ???
    search_fields = ['company__name','id','container__title','items__product__title','items__product__type__title']
    save_on_top = True
    #listviewtitle = 'custom title - list view' # place holder
    ordertitle = True
    suppress_form_controls = {
        'show_save_and_add_another': False,
        'show_delete': False,
        'show_save': False,
     #   'title': title
    }
    list_display = ['id','company','container_link']
    fields = ['xmanufacture_notes','xdelivery_notes'] # ('id','company', 'key_date') -> are in page title
    readonly_fields = ['xmanufacture_notes','xdelivery_notes','created_at','modified','company','id']
    class Media:
        pass #js = ('erp/q.js',)
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    def has_add_permission(self, request, obj=None):
        return False
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    #date_hierarchy = 'MD'
    def jobs_done(self, obj):
        return 
    def jobs_todo(self, obj):
        return 
    def container_link(self, obj): 
        if obj:
            return container_link(obj.container)

