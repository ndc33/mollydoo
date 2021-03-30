#------------inherited by works views-----------------

from django import forms
from django.db import models # only used on annotations
from django.db.models import Q, F, Count
from django.contrib import admin
#from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
#from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

import operator
from functools import reduce

from .setup import erp_admin, site_proxy, name_proxy, TabularInline
from .setup import text_box, batch_link, product_link, company_link

from totalsum.admin import TotalsumAdmin
from ..models import ProductDisplayCategory
from ..models import OrderItemProxy  #, OrderItem
from ..models import SpecNote, OrderNoteItem
from ..models import ccc
from ..utils import  ss, setwidget, decorate, work_field_names #work_field_names_plural,
from ..utils import get_related_field



def set_item_complete(instance, process_list):
    if process_list == ['all']:
        process_list = work_field_names
    for process in process_list:
        #import pdb; pdb.set_trace()
        if getattr(instance.product.type, f'{process}'):
            remain = getattr(instance, f'{process}_remain2')
            tally = getattr(instance, f'tally_{process}')
            if not '-' in tally: # not robust
                setattr(instance, f'tally_{process}', f'{tally},,{remain}')
                setattr(instance, f'{process}_total', instance.quantity) # not robust
    #instance.save()  # added for the action
    

   
class OrderItemForm(forms.ModelForm):
    force_complete = forms.BooleanField(label='force complete', required=False)
    class Meta:
        model = OrderItemProxy
        fields = '__all__'
    def save(self, commit=True):
        if self.cleaned_data['force_complete']:
            instance = super().save(commit=False)
            set_item_complete(instance, work_field_names) # or ['all']
            #commit = True
            #instance.save()
            #import pdb; pdb.set_trace()
        super().save(commit=True)
        #if commit:
    


class WorksTemplateInline(TabularInline):
    model = OrderItemProxy  
    extra = 0
    description = True #?
    form = OrderItemForm
    class Media:
        css = {'all': ('erp/hide_inline_title.css',)}
        #js = ('erp/collapse_open.js',)
    def has_add_permission(self, request, obj=None):   # called 1st before delete permissions
        process = self.parent_model.process 
        if process == 'all':
            # hacked on here in permissions to access 'self', self.process 
            self.verbose_name_plural = 'Order Items - Operations Remaining to Complete' # inline title bar
        else:
            self.verbose_name_plural = 'Items to ' + process 
        return False 
    def has_delete_permission(self, request, obj=None):
        self.model.process = self.parent_model.process ####### fixme ******* botch *********************************
        return False
    def get_fieldsets(self, request, obj=None):     # example                                                                 
        return super().get_fieldsets(request, obj)  
    def get_queryset(self, request): 
        qs = super().get_queryset(request)
        process = self.parent_model.process #self.model.process 
        #if hasattr(self, 'process_lookup'): used to be defined in worksviews
        #    qs = qs.filter(**{self.process_lookup : True})
        if not process == 'all': 
            qs = qs.filter(**{'product__type__' + process: True})
        return qs
    def get_readonly_fields(self, request, obj=None):
        process = self.parent_model.process #self.model.process 
        ptype = '__product__type__title__(type)' #'type'
        if process == 'all':
            wft = [f'__{wfd}_remain2__({wfd})' for wfd in work_field_names]
            default = ['product_link', ptype,'quantity','progress', *wft]
        else:
            default = ['product_link', ptype,'quantity_html','overprints', 
            'xnotes', 'remain', 'total_html','print_locations','pp','note_html']#, process + '_note']
        return default
    def get_fields(self, request, obj=None):
        process = self.parent_model.process #self.model.process 
        ptype = '__product__type__title__(type)' #'type'
        if process == 'all':
            #import pdb; pdb.set_trace()
            wft = [f'__{wfd}_remain2__({wfd})' for wfd in work_field_names]
            default = ['product_link',ptype,'quantity','progress', *wft,'force_complete'] #,'__ppp','order__qqqq'
        else:
            default = ['product_link', ptype,'quantity_html', 'note_html',# process + '_note', 
                f'tally_{process}', 'total_html','remain'] #'xnotes'
        if process in ['pcut', 'weld']: 
            default.insert(3, 'print_locations')
        if process == 'print':
            default.insert(3, 'overprints')
        return default
    """def queryset(self, request, queryset):
        process = self.parent_model.process
        if self.value() is None:
            return queryset
        vv = {'product__type__'+process:True}
        return queryset.filter(**vv) # note the trick """
    # added 19/03
    def total_html(self, obj):
        process = self.parent_model.process
        total = getattr(obj, process + '_total')
        qty = obj.quantity
        color = 'ff0000' if total > qty else '787878'
        #import pdb; pdb.set_trace()
        html = format_html('<span style="font-weight:bolder;color:#{};">{}</span>', color, total)
        #html = format_html('<b>{}</b>', getattr(obj, process + '_total')) 
        return html
    total_html.short_description = 'Total'
    def note_html(self, obj):
        process = self.parent_model.process
        condition = None if process == 'all' else Q(process=process)|Q(process='all')
        qq = obj.product.productnotes.filter(condition).values_list('note', flat=True)
        qq = ''.join('%s <text:line-break /> ; ' % q for q in qq)[0:-2] # to kill final ';'
        return format_html(qq) if qq else '-'
    note_html.short_description = 'Notes'
    def remain(self, obj):
        #import pdb; pdb.set_trace()
        process = self.parent_model.process
        tmp = getattr(obj, process + '_remain2')
        return format_html('<span style="color: #{};">{}</span>', '787878', tmp)
    def product_link(self, obj): 
        #import pdb; pdb.set_trace() # fixme - process coming through as 'all'
        process = self.parent_model.process
        if process == 'all':
            complete = not 100-int(getattr(obj, f'progress2'))
        else:
           complete = not getattr(obj, f'{process}_remain2')
        if obj:
            style = "text-decoration:line-through" if complete else "font-weight:bold" #fixme
            return product_link(obj.product, style)

 

    
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
    def __getattr__(self, attr):
        if '__' in attr:
            return get_related_field(attr)
        return self.__getattribute__(attr)
    # NOTE the 5 vars here used as directives, they are used throughout 
    remove_pk_controls = []
    listviewtitle = None
    suppress_form_controls = {}
    producttitle = False
    ordertitle = False
    modify_labels = {}
    def has_delete_permission(self, request, obj=None):
        if 'popup' in request.path:
            import pdb; pdb.set_trace()
        return False
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
            pass
        for field in form.base_fields: # keep for info
            # Note from docs: the label suffix is added only if the last character of the label isn’t a punctuation character
            if form.base_fields.get(field).required:
                form.base_fields.get(field).label_suffix = ' *:' # for play/example only
        return form
    def changelist_view(self, request, extra_context=None):
        if self.listviewtitle: # todo finish
            color = '000000'#'787878'
            qq = format_html(
                #('{} <span style="color: #{};">&nbsp<sub>{}</sub></span>'
            '<span style="color: #{};">{}</span>',
            color,
            self.listviewtitle,
            )
            extra_context = {'title': qq}#self.listviewtitle} # 'show_save': False not working here
        return super().changelist_view(request, extra_context=extra_context)
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # see the follwing to deal with popups
        # https://stackoverflow.com/questions/49560378/cannot-hide-save-and-add-another-button-in-django-admin
        context.update({
            'show_save': False,
            #'show_save_and_continue': False,
            'show_save_and_add_another':False,
            'show_delete': False
        })
        return super().render_change_form(request, context, add, change, form_url, obj)
    



class OrderNoteItemInline(admin.TabularInline):
    model = OrderNoteItem
    verbose_name_plural = 'Order Notes'
    extra = 0
    formfield_overrides = text_box(1, 30)
    def get_fields(self, request, obj=None):
        process = self.parent_model.process
        if process == 'all':
            return ['process', 'note_html']
        return ['note_html']
    readonly_fields = ['process', 'note_html']
    # def process(self, obj):
    #     return obj.ordernote.process
    # def note(self, obj):
    #     return obj.ordernote.note
    def has_add_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def get_queryset(self, request):
        process = self.parent_model.process
        qs = super().get_queryset(request)
        if not process == 'all':
            qs = qs.filter(Q(process=process)|Q(process='all'))
        return qs
    
class BasisOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if 'batch' in self.fields:
            self.fields['batch'].widget.can_change_related = False
            self.fields['batch'].widget.can_delete_related = False
        if 'batch' in self.base_fields:
            self.base_fields['batch'].widget.can_change_related = False
        # if hasattr(self, 'modify_labels'):
        #     for key,value in self.modify_labels.items():
        #         # overwrite labels
        #         self.base_fields[key].label = value 

       

class BasisOrderTemplate(admin2):
    # def __init__(self, *args, **kwargs):
    #     self.process = kwargs['process'] #self.model.process
    #     super().__init__(*args, **kwargs)
    form = BasisOrderForm
    #remove_pk_controls = ['batch']
    autocomplete_fields = ['batch']
    search_fields = ['company__name','id','batch__title','items__product__title','items__product__type__title']
    #save_on_top = True
    #listviewtitle = 'custom title - list view' # place holder
    #ordertitle = True
    # suppress_form_controls = {
    #     'show_save_and_add_another': False,
    #     'show_delete': False,
    #     'show_save': False,
    #  #   'title': title
    # }
    class Media:
        css = {'all': ('erp/label_width.css', )}
        pass #js = ('erp/q.js',)
    def order_complete_action(self, request, queryset):
        process = self.model.process
        for _order in queryset:
            for item in _order.items.all():
                set_item_complete(item, [process])
                item.save()
    order_complete_action.short_description = "Force Complete the select(ed) Orders"
    actions = ['order_complete_action'] 
    """def get_actions(self, request):
        actions = super().get_actions(request)
        process = self.model.process
        if not process == 'all':
            del actions['order_complete_action']
        return actions"""
    def has_add_permission(self, request, obj=None):   # this fires 4th for listview and 5th or 6th for details
        process = self.model.process     
        return False#True if process == 'all' else False
    def has_change_permission(self, request, obj=None):   # fires before add_permission on details and listview 
        process = self.model.process     
        return True #if process == 'all' else False # false kills the tally input
    def get_queryset(self, request):   # fired 3rd for listview, 1st for detailsview 
        qs = super().get_queryset(request)
        html = format_html('<span style="color: #{};">{}</span>', '008000', 'sssgreen')
        qs = qs.annotate(sss=models.Value(html, output_field=models.TextField())) # testing
        return qs
    #date_hierarchy = 'MD'
    def jobs_done(self, obj):
        return 
    def jobs_todo(self, obj):
        return 
    def batch_link(self, obj): 
        if obj:
            return batch_link(obj.batch)
    def get_inlines(self, request, obj=None):   # fires 5th for details
        return [OrderNoteItemInline, WorksTemplateInline] 
    def totals_sum(self, obj): # used for totals summaries
        process = self.model.process
        if process == 'all':
            vv = ccc('__productcategory_quantity__({category},{category})')
        else:
            vv = ccc('__productcategoryprocess_remain__({category},'+process+',{category})')
            #vv = ccc('__productcategoryprocess_remain_qs__({category},'+process+',{category})')
        return vv
    def get_list_display(self, obj):  # this firest 2nd for list view   
        #vv = ['id','company'] + self.model.category_titles +['OD','batch_link'] # old
        process = self.model.process
        if process == 'all':
            self.list_editable = ['batch']
            vv = ccc('__productcategory_quantity__({category},1,{category})')
            vv =  ['id','company'] + vv + ['OD','batch']
        else:
            vv = ccc('__productcategoryprocess_remain__({category},'+process+',1,{category})')
            vv =  ['id','company'] + vv + ['OD','batch_link']
            #testing: vv = ccc('__productcategoryprocess_remain_qs__({{category}},{process},1,{{category}})'.format(process=process))
        #vv = self.model.category_titles # to test old behavior
        return  vv 
    
    def get_readonly_fields(self, request, obj=None):  # fires 4th for detailsview
        process = self.model.process
        if process == 'all':
            vv = ['OD', 'LD_markup','CD_markup','id','company_link','batch_link']
        else:
            vv = ['id','company','batch_link']
        return vv
    def get_fields(self, request, obj=None):  # fires 3rd for detailsview
        process = self.model.process
        if process == 'all':
            vv = [('id','company_link','batch_link'),'batch',('OD','LD_markup','CD_markup')] 
        else:
            vv= [('id','company','batch_link')]
        return vv
    def changelist_view(self, request, extra_context=None):  #this fires 1st for listview
        process = self.model.process
        # self.totalsum_list = self.model.totalsum_list
        var = '{} &nbsp&nbsp&nbsp <small><sup>{}<span style="color: #{}</sup>;">&nbsp<sub>{}</sub></small></span>'
        if process == 'all':
            qq = format_html(var, 'Operations Orders','Total Items','787878','%Progress')
            qq = mark_safe(qq) # todo cannot get rid os markup showing
        else:
            qq = format_html(var, process.capitalize()+' Orders','items remaining','787878','of total')
        extra_context = {'title': qq}
        return super().changelist_view(request, extra_context=extra_context)
    def change_view(self, request, object_id, form_url='', extra_context=None): #new
        process = self.model.process
        extra_context = {'title': f'{process.upper()} Order {object_id}'}
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    """def get_fieldsets(self, request, obj=None):   # example  
        # fired 2nd for detailsview                                                   
        return super().get_fieldsets(request, obj) 
    def get_form(self, request, obj=None, **kwargs):  # example
        form = super().get_form(request, obj, **kwargs) 
        return form"""
    def get_search_results(self, request, queryset, search_term):
        '''needs a lot of work'''
        # search_term is what you input in admin site, queryset is search results
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        search_term_list = search_term.split(',')
        #search_term_list = [term for term in search_term_list if term.isdigit()]
        if  len(search_term_list)<2:
            return queryset, use_distinct
        #import pdb; pdb.set_trace()
        # you can also use `self.search_fields` instead of following `search_columns`
        # __icontains fixes the int error and is necessary for print case
        search_columns = ['id','items__product__type__title']
        #convert to Q(name='x') | Q(name='y') | ...
        query_condition = reduce(operator.or_, [Q(**{c+'__icontains':v}) for c in search_columns for v in search_term_list])
        queryset = self.model.objects.filter(query_condition)
        # NOTICE, if you want to use the query before
        # queryset = queryset.filter(query_condition)
        return queryset, use_distinct
    def company_link(self, obj): 
        return company_link(obj.company)
    
    """ # alternative experiment
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        search_term_list = search_term.split(',')
        search_term_list = [term for term in search_term_list if term]
        if not search_term_list: #any(search_term_list):
            return queryset, use_distinct
        for term in search_term_list:
            try:
                term = int(term)
            except ValueError:
                pass # assume string use against type
                #import pdb; pdb.set_trace()
                qs = self.model.objects.filter(items__product__type__title__icontains=term)
                queryset |= qs
            else: # no exception
                queryset |= self.model.objects.filter(id=term)
        return queryset, use_distinct
    """
    
   

