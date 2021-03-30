
# codegen - origionally used for get_inlines
'''OrderItemProxy is the proxy to OrderItem'''
###kk = create_model(name=self.process+'item', model=OrderItemProxy, kwargsextra={'process':self.process})
'''create a new model based on WorksTemplateInline with the model set to the new OrderItemProxy'''
###vv = type('xyz', (WorksTemplateInline,), {'model':kk,'process':self.process})#OrderItemPrint}) # codegen
###return [OrderNoteItemInline, vv] # origional = WorksPrintInline


#class OrderItemInlineFreeKey(OrderItemInline):
#    pass
    ################ temp test
    '''class OrderItemInlineFreeKey(admin.StackedInline):
    model = OrderItemAdminView
    extra = 0
    formfield_overrides = text_box(1, 30)
    #fields = ('product','qnotes','xprice','quantity')
    #readonly_fields = ['qnotes']
    #fields = ('product','xnotes','xprice','quantity')
    #fields = (('product', 'xprice','quantity'),('xprint_notes','xcut_notes','xpack_notes'))
    class Media:
        css = {'all': ('erp/hide_inline_title.css', )}
    myobject_id = None
    #################temp
    '''
#from admin2
# def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
    #     if (self.producttitle): # override title (since obj required)
    #         self.suppress_form_controls['title'] = '%s of %s' % (obj.quantity, obj.product)
    #     if (self.ordertitle): # override title (since obj required)
    #         #import pdb; pdb.set_trace()
    #         if P := getattr(obj, 'process',None):
    #             self.suppress_form_controls['title'] = f'Works Order <<{P.upper()}>>'
    #         """try: 
    #             batch_title = obj.container__title
    #         except:
    #             batch_title = None
    #         # ugly botch to fit with current architecture
    #         self.suppress_form_controls['title'] = mark_safe(
    #             '%s%s Order: %s%s Batch: %s' % 
    #             (obj.company.name, ss*18, obj.id, ss*36, obj.container)
    #             )"""
    #     context.update({**self.suppress_form_controls})
    #     return super().render_change_form(request, context, add, change, form_url, obj)

# from initite generated classes


 # suppress_form_controls = {
    #     'show_save_and_add_another': False,
    #     'show_delete': False,
    #     'show_save': False
    # }




"""

from ..models import Order, OrderItemRelatedModelMethods, ProductDisplayCategory, OrderItemRelatedModelMethods
from django.db.models import Q, F, Count, Avg
from django.utils.html import format_html
from ..utils import work_field_names
#from .worksviews import WorksOrderTemplate 
# -----

# *** ugly patch, raw code executed on import so placed here to allow models 
# to be created on startup (we require ProductCategories)
# also server requires restart to update changes of ProductCategories

## WorksOrderAdminall' object has no attribute 'PVC_Weld_progress_all_totals'
ProductCategories = ['cm'] list(ProductDisplayCategory.objects.values_list('title', flat=True))

# from Order
def productcategory_quantity(self, product_category, withprogress=False):
    '''basis for enumerated method generation (see below) such as CM_remain_weld 
        or (with progress) ARM_progress_all'''
    # core of this could be done directly on query (not worth effort)
    total_quantity = total_progress = hasresult = 0
    items = self.items.all() #yyy
    #items = self.items.filter(product__type__category__title=product_category)#.all()
    for item in items:
        #import pdb; pdb.set_trace()
        if product_category == item.product.type.category.title: #kk
            qty = item.quantity
            total_quantity += qty
            total_progress += item.item_progress * qty
            hasresult = True
    if hasresult:
        total_progress = total_progress/total_quantity if total_quantity else ''
        if withprogress:
            #return '%s of %s' % (total_quantiy, total_progress)
            total_progress = '{0:.0f}%'.format(total_progress) #if total_progress else '0%'
            color = '585858'
            return format_html('{} <span style="color: #{};">&nbsp<sub>{}</sub></span>', total_quantity, color, total_progress)
        return total_quantity
    return '-'
def productcategoryprocess_remain(self, product_category, process, withtotals):
    '''basis for enumerated method generation (see below) such as CM_total_all'''
    remain_total = qty_total = 0
    hasresult = False
    for item in self.items.all():
        if product_category == item.product.type.category.title: #kk
            import pdb; pdb.set_trace()
            remain_subtotal = getattr(item, process + '_remain')
            qty_subtotal = item.quantity
            if isinstance(remain_subtotal, int):
                #print(product_category, process, subtotal)
                remain_total += remain_subtotal
                qty_total += qty_subtotal
                hasresult = True
    if hasresult:
        if withtotals:
            #return '%s of %s' % (remain_total, qty_total) 
            color = '585858'
            return format_html('{} <span style="color: #{};"><sub>of {}</sub></span>', remain_total, color, qty_total)
        else: 
            return remain_total 
    return '-'

def product_process_class_methods(cls, product_category, process, method_name, withtotals=False):
    def innerfunc(self):
        return productcategoryprocess_remain(self, product_category, process, withtotals)
    innerfunc.__name__ = method_name
    setattr(innerfunc, 'short_description', product_category)
    setattr (cls, innerfunc.__name__, property(innerfunc))
for process in work_field_names:
    ''' create methods e.g. CM_remain_weld'''
    #import pdb; pdb.set_trace()
    for product_category in ProductCategories: 
        method_name = product_category + '_remain_' + process
        product_process_class_methods(Order, product_category, process, method_name, True)
######

for process in work_field_names:
    #  # crude and inefficient hack implimented
    ''' create methods e.g. CM_remain_weld_totals for the total summary row'''
    for product_category in ProductCategories: 
        method_name = product_category + '_remain_' + process +'_totals'
        product_process_class_methods(Order, product_category, process, method_name, False)

#---

def product_total_class_methods(cls, product_category, method_name, withprogress=False):
    def innerfunc(self):
        return productcategory_quantity(self, product_category, withprogress)
    innerfunc.__name__ = method_name
    setattr(innerfunc, 'short_description', product_category) 
    setattr (cls, innerfunc.__name__, property(innerfunc))
for product_category in ProductCategories: 
    '''e.g. ARM_total_all'''
    method_name = product_category + '_total_all'
    product_total_class_methods(Order, product_category, method_name, False)

for product_category in ProductCategories: 
    '''e.g. ARM_progress_all'''
    method_name = product_category + '_progress_all'
    product_total_class_methods(Order, product_category, method_name, True)

#######
for product_category in ProductCategories: 
    # crude and inefficient hack implimented
    '''e.g. ARM_progress_all_totals for the total summary row'''
    method_name = product_category + '_progress_all_totals'
    product_total_class_methods(Order, product_category, method_name, False)


# copied from OrderItemRelatedModelMethods
def processnote(self, process):
    '''basis for enumerated method generation (see below) such as print_note'''
    #import pdb; pdb.set_trace() 
    # will not honour newlines
    qq = self.product.productnotes.filter(
        Q(process=process)|Q(process='all')
        ).values_list('note', flat=True)
    qq = ''.join('%s <text:line-break /> ; ' % q for q in qq)[0:-2] # kill final ';'
    qq2 = format_html(qq) if qq else ''
    return qq2 #list(qq) or ''


def orderitem_processnotes_class_methods(cls, process, method_name):
    def innerfunc(self):
        return processnote(self, process)
    innerfunc.__name__ = method_name
    #setattr(innerfunc, 'short_description', product_category)
    setattr (cls, innerfunc.__name__, property(innerfunc))

for process in work_field_names:
    ''' create methods e.g. print_note'''
    method_name = process + '_note'
    orderitem_processnotes_class_methods(OrderItemRelatedModelMethods, process, method_name)
"""




# from change list totals

""" 
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList


class ChangeListTotals(ChangeList):
    def get_results(self, *args, **kwargs):
        super(ChangeListTotals, self).get_results(*args, **kwargs)
        if hasattr(self.model_admin, 'list_totals'):
            self.aggregations = []
            list_totals = dict(self.model_admin.list_totals)
            for field in self.list_display:
                if field in list_totals:
                    self.aggregations.append(
                        self.result_list.aggregate(agg=list_totals[field](field))['agg'])
                else:
                    self.aggregations.append('')


class ModelAdminTotals(admin.ModelAdmin):
    #change_list_template = 'admin_totals/change_list_totals.html'
    change_list_template = 'change_list_totals.html'

    def get_changelist(self, request, **kwargs):
        return ChangeListTotals
"""

# from company 

# #@admin.register(Address, site=site_proxy)
# class AddressHistoryAdmin(SimpleHistoryAdmin): 
#     # https://django-simple-history.readthedocs.io/en/2.12.0/history_diffing.html
#     list_display = ["id", "name"]#, 'changed_fields']
#     #history_list_display = ["status"]
#     #search_fields = ['name', 'user__username']
#     #history_list_display = ['changed_fields']

#     def changed_fields(self, obj):
#         if obj.prev_record:
#             delta = obj.diff_against(obj.prev_record)
#             #return delta.changed_fields # origional stackoverflow
#             return delta.changes.field
#         return None
# # type, name, address, postcode

# admin.site.register(Address, AddressHistoryAdmin, site=site_proxy)


# from products 

"""class ProductLineItems(OrderItemInline):
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
         return False"""
