
# utils origionally used when running into circular references for the first time. May rework 
#from django.db import models
import regex as rex
import datetime
from django.utils.html import format_html
from django.utils.safestring import mark_safe
#from .models import ProductCategory

ss = "&nbsp"

work_field_names = ['print','pcut','weld','cut','glue','stuff','pack']
#work_field_names_plural = {'print':'printed','cut':'cut','weld':'welded','stuff':'stuffed','pack':'packed'}
# alternative Query for above ProductType._meta.get_field('category').choices


def create_model(model, name, kwargsextra={}):
    ''' e.g. vv = create_model(name='dynamic1', model=TestDynamic, {process:'print'})'''
    class Meta:
        proxy = True
        app_label = model._meta.app_label #'erp'
        verbose_name_plural = kwargsextra['verbose_name_plural']
        # model._meta.label_lower
    attrs = {'__module__': '', 'Meta': Meta,**kwargsextra}
    newmodel = type(name, (model,), attrs)
    #admin.site.register(newmodel, modeladmin)
    return newmodel #modeladmin


def get_related_field(name, admin_order_field=None, short_description=None):
    '''dynamic access to model and related model 
        1) model and admin methods 
        2) model and admin functions 
        3) query annotations etc
        used in admin list_display strings, details view read_only fields etc
        a) can call method e.g. '__method_on_same_object'
        b) method on related object '__relatedModel__method'
        c) can call with fuction args '____relatedModel__method__(arg1, short_name)'
        ** the last arg on function call is allways the shortname (ignored as function arg) **
        d) hence can call a method and add the shortname '__method__(short_name)'
        e) can also call argless functions '__querysetname__count__(,short_name)' 
        f) <name>__html (now redundent) to get html markup contained in the annotation'''
    #@property
    html = None
    farg = None
    column_title = None
    title =False
    def _html(value): # not used
        return mark_safe(value)
    related_names = [x for x in name.split('__') if x]
    #rcopy = 
    if related_names[-1] == 'html':
        html = related_names.pop() 
    if related_names[-1].startswith('('):
        farg = related_names.pop()[1:-1].split(',')
        column_title = farg.pop()
    def dynamic_attribute(obj):
        for related_name in related_names:
            #import pdb; pdb.set_trace()
            obj = getattr(obj, related_name) #()
        if farg:
            if farg==['']:
                return mark_safe(obj())
            return mark_safe(obj(*farg))
        return _html(obj) if html else mark_safe(obj) # with mark_safe on all no longer require html function
    if name == '':
        import pdb; pdb.set_trace()
    # fixme admin_order_field broken
    #if not farg == ['']: # testing
    #    print(name)
        #import pdb; pdb.set_trace()
    title = '__'.join(related_names)
    dynamic_attribute.admin_order_field = title or name #admin_order_field or '__'.join(related_names) #name
    dynamic_attribute.short_description = short_description or column_title or related_names[-1].title().replace('_', ' ')
    return dynamic_attribute


def decorate(**kwargs):
    def wrap(function):
        for name, value in kwargs.items():
            setattr(function, name, value)
        return function
    return wrap


def _sumtally(s): # called indirectly by sumtally below
    """ can accept strings like folllowing for job tally's '9,7,  1,,2,,,8' """ 
    total = 0
    if s:
        for i in s.split(','):
            i = i.strip(', ')
            if not i:
                i = 0
            total += int(i)
    return total

regex_roll_tally = rex.compile(r'[Rr](\d+)[(]([\d,]+)[)]', rex.MULTILINE)

regex_error = rex.compile(r"""          # needs completly rewriting, will do for now
                   (?:[^0-9rR ,\(\)])   # restricted symbols 
                   |([rR,]\()           # open bracket logic = not 'r(' or '(' i.e. missing roll number
                   |[\d\)\()][rR]       # r logic = not 'xr' where x is number, ')' or '(' i.e. missing ','
                   |\)[rR\d\(] # close bracket logic = not ')x' where x is a number or 'r'
                   """, rex.VERBOSE | rex.MULTILINE)

def sumtally(s):
    try:
        qq = regex_error.search(s)
        if qq:
            return 'error in tally, see: ' + qq.group() 
        vv = _sumtally(s)
        #import pdb; pdb.set_trace()
        return vv
    except:
        return 'error in tally'


def get_roll_groups(text):
    """ accepts strings like following for tracking prints to rolls '9  ,r67(8,9,8),r2(3),9,r67(4)' """ 
    try:
        #import pdb; pdb.set_trace() 
        qq = regex_error.search(text)
        if qq:
            return ('error in tally, see: ' + qq.group(), 'error')
        rgx_list = regex_roll_tally.finditer(text)
        ff = []
        total = 0
        new_text = text
        for rgx_match in rgx_list:
            new_text = rex.sub(rex.escape(rgx_match.group(0)), '', new_text)
            ff.append(['R'+rgx_match.group(1),rgx_match.group(2)])
            #print(rgx_match.group())
        ff.append(['other',new_text])
        roll_names = [i for i,_ in ff]
        roll_sum = dict([k, 0] for k in set(roll_names))
        for k, v in ff:
            subtotal = _sumtally(v)
            roll_sum[k] += subtotal
            total += subtotal
    except:
        return ('error in tally', 'error')
    return (int(total), roll_sum)


def setwidget(widget, attr = None):
    if attr:
        if 'change' in attr:
            widget.can_change_related = False
        if 'add' in attr:
            widget.can_add_related = False
        if 'delete' in attr:
            widget.can_delete_related = False
        pass
    else:
        widget.can_add_related = False
        widget.can_change_related = False
        widget.can_delete_related = False


def shortdate(obj):
    if isinstance(obj, datetime.date):
        return obj.strftime("%a %d %b")
    return obj



