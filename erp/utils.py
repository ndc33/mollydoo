
# utils origionally used when running into circular references for the first time. May rework 

ss = "&nbsp"

work_field_names = ['print','cut','weld','stuff','pack']

def decorate(**kwargs):
    def wrap(function):
        for name, value in kwargs.items():
            setattr(function, name, value)
        return function
    return wrap


def sumtally(s):
    #import ipdb; ipdb.set_trace() 
    total = 0
    try:
        if s:
            for i in s.split(','):
                #any(x in a_string for x in matches)
                i = i.strip(', ')
                if not i:
                    i = 0
                total += int(i)
    except:
        total = 'error in tally'
    return total


def setwidget(widget):
    widget.can_add_related = False
    widget.can_change_related = False
    widget.can_delete_related = False

