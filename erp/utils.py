
# utils origionally used when running into circular references for the first time. May rework 
import regex as rex
import datetime

ss = "&nbsp"

work_field_names = ['print','cut','weld','stuff','pack']
ProductCategories = ['CM','ARM','XPVC','M','SPRUNG','OTHER'] 
# alternative Query for above ProductType._meta.get_field('category').choices

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
        #import pdb; pdb.set_trace() 
        qq = regex_error.search(s)
        if qq:
            return 'error in tally, see: ' + qq.group()
        return _sumtally(s)
    except:
        return 'error in tally'

def get_roll_groups(text):
    """ accepts strings like folllowing for tracking prints to rolls '9  ,r67(8,9,8),r2(3),9,r67(4)' """ 
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


def setwidget(widget):
    widget.can_add_related = False
    widget.can_change_related = False
    widget.can_delete_related = False

def fixdate(obj):
    if isinstance(obj, datetime.date):
        return obj.strftime("%a %d %b")
    return obj

