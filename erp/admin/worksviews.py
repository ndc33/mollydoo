from .setup import erp_admin, site_proxy, name_proxy
from ..models import Order
from ..models import ccc
from .workstemplate import BasisOrderTemplate

from ..utils import create_model, work_field_names


for process in work_field_names + ['all']: # ['print','weld','cut', 'all']: # codegen
    admin_model = type(f'WorksOrderAdmin{process}', (BasisOrderTemplate,), {}) 
    order_proxy = create_model(name=f'Order{process}', model=Order, 
        kwargsextra={'process':process,
        'verbose_name_plural':f'Works Order {process}'
    }) 
    erp_admin.register(order_proxy, admin_model)  # , site=site_proxy)



# -------------------------

"""

 # if process == 'all': # ops
    #     category_titles = ccc('{category}_progress_all') 
    # else:
    #     category_titles = ccc('{category}_remain_'+process)
    #totalsum_list = [w+'_totals' for w in category_titles]

   #'category_titles':category_titles,
        #'totalsum_list':totalsum_list,

#@admin.register(OrderPrint, site=site_proxy)
class WorksPrintOrderAdmin(WorksOrderTemplate):
    ''' process here is the master definition''' # but also defined on the order proxy
    # process = 'print' 
    #category_remain_process = ccc('{category}_remain_'+process)
    # totals_summary_row = [w+'_totals' for w in category_remain_process]
    # totalsum_list =  totals_summary_row
    pass
erp_admin.register(OrderPrint, WorksPrintOrderAdmin) # OrderPrint"""


#@admin.register(OrderOps, site=site_proxy)
#class OpsAdmin(BasisOrderTemplate):#WorksOrderTemplate):
#    passs