from django.contrib import admin
from django.contrib.admin.utils import label_for_field
from django.db.models import Sum
from django.core.exceptions import FieldDoesNotExist


class TotalsumAdmin(admin.ModelAdmin):
    change_list_template = "totalsum_change_list.html"
    totalsum_list = ()
    unit_of_measure = ""
    totalsum_decimal_places = 2
    
    def changelist_view(self, request, extra_context=None):
        response = super(TotalsumAdmin, self).changelist_view(request, extra_context)
        if not hasattr(response, "context_data") or "cl" not in response.context_data:
            return response
        filtered_query_set = response.context_data["cl"].queryset
        extra_context = extra_context or {}
        extra_context["totals"] = {}
        extra_context["unit_of_measure"] = self.unit_of_measure
        #import pdb; pdb.set_trace()
        if hasattr(self, 'totals_sum'): # added nc
            self.totalsum_list = self.totals_sum(self)
        #for elem in getattr(self, 'totals_sum', self.totalsum_list): x function not method
        for elem in self.totalsum_list:
            try:
                self.model._meta.get_field(elem)  # Checking if elem is a field
                total = filtered_query_set.aggregate(totalsum_field=Sum(elem))[
                    "totalsum_field"
                ]
                if total is not None:
                    extra_context["totals"][
                        label_for_field(elem, self.model, self)
                    ] = round(total, self.totalsum_decimal_places)
            except FieldDoesNotExist:  
                # maybe it's a model property (or later just search on the adminmodel i.e. self)
                #import pdb; pdb.set_trace()
                #entity = self # changed from self.model
                # label failing for annotations (annotations are dealt with here)

                try:
                    '''this is a method on the model'''
                    #if hasattr(self.model, elem): # changed from self.model
                    total = 0
                    fired = False
                    for f in filtered_query_set:
                        qq = getattr(f, elem)#, 0)
                        if not qq == '-':
                            total += qq
                            fired = True
                    if fired:
                        extra_context["totals"][
                            label_for_field(elem, self.model, self) # origional self.model
                        ] = round(total, self.totalsum_decimal_places)
                except AttributeError:  # added
                    '''this is a function on the admin, we pass the query item as the obj argument'''
                    #xelem = elem+'_totals' # what for??
                    #if hasattr(self, xelem):
                    try:
                        total = 0
                        fired = False
                        for f in filtered_query_set:
                            qq = getattr(self, elem)(f)
                            if not qq == '-':
                                #import pdb; pdb.set_trace()
                                #if isintance(qq,str) and qq
                                total += int(qq)
                                fired = True
                        if fired:
                            extra_context["totals"][
                                label_for_field(elem, self.model, self)
                            ] = round(total, self.totalsum_decimal_places)
                    except:
                        pass # fixme - check origional behavior

        response.context_data.update(extra_context)
        return response
