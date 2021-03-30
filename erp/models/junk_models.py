 var = self.items.filter(
            Q(order__id = self.id) &
            Q(category=product_category) 
            ).aggregate(sum=Sum(F(f'{process}_remain2'), 
            output_field=IntegerField())
            )
            # .aggregate(qty=Sum(F('quantity'), 
            # output_field=IntegerField())
            # )
            #
            remain_total = var["sum"]
            qty_total = var['qty']
        if remain_total is None:  # distiguish from zero 
            return '-'
        if withtotals: 
            #return '%s of %s' % (remain_total, qty_total) 
            return format_html('{} <span style="color: #{};"><sub>of {}</sub></span>', remain_total, '585858', qty_total)
        else: 
            return remain_total 
  
  
  
  # replaced with copy_and_create_order_notes()
  #company = Company.objects.get(id=self.company_id)
  """company_ordernotes = company.ordernotes.all()
            commonfields = OrderNoteAbstract._meta.fields
            for note in company_ordernotes:
                fields = model_to_dict(note, fields=[f.name for f in commonfields])
                #import pdb; pdb.set_trace()
                fields['order'] = self
                OrderNoteItem.objects.create(**fields)
                #pp = OrderNoteItem(**fields)
                #pp.save()"""
    
# order annotation junk ----------------------
   
            #.annotate(
             #   **{f'sumpp_{category}':Sum('items__progress2', filter=Q(items__product__type__category__title=category)) 
             #       for category in categories}  
                #**{f'sumpp_{category}':Sum('items__progress2', filter=Q(items__product__type__category__title=category)) 
                #    for category in categories} 
                    #Func('lines__gross_amount', function='SUM',)
             #   progress=ExpressionWrapper(Sum(F('items__progress2') * F('items__quantity')), output_field=models.FloatField())
              #reduce(operator.add, (F('items__progress2') for category in categories))
            #)
        #import pdb; pdb.set_trace()
        #qs = qs.prefetch_related('items__product', 'items__product__type', 'items__product__type__category')#items__product__type
        #qs = qs.select_related('container')
        #qs = qs.select_related('batch')
        #all_product_types_defined = ProductType.objects.values_list('code', flat=True)
        ###all_product_types_defined = ProductType.objects.values('code')
        ###qs = qs.annotate(all_product_types_defined=all_product_types_defined)
        
        # the following both work
        #qs = qs.all().annotate(qqq=models.Value('order all qqq annotation', output_field=models.CharField())) # testing

     #qs = qs[:].annotate(qqq=models.Value('qqq2 annotation', output_field=models.CharField()))
        #product__type__category__title
        
        # 'item', 'item__product' makes no difference

    #operations_sum_exp = reduce(operator.add, (F(f'{process}_total') for category in categories))
        #Count('book', filter=Q(book__rating__gt=5))
        # **{f'sum_{category}':Sum('quantity', filter=Q(items__product__category__title=category))) 
        #            for category in categories}

#from orderitem annotation junk ---------------------------

 #{f'{process}_total':F('quantity')-F(f'{process}_total') 
        #    for process in work_field_names}
        #remain_dict = {}
        #for process in work_field_names:
        #    remain_dict[f'{process}_remain2'] = F('quantity')-F(f'{process}_total')
        #qs = qs.annotate(**remain_dict)
        #qs = qs.annotate(_ppp=models.Value(1, output_field=models.IntegerField())) # testing

         #qs = qs.objects.annotate(xremain=F('quantity') - F('num_chairs')
        #qs = qs.prefetch_related(models.Prefetch('order__DD'))
        #qs = qs.select_related('order__batchorders__batch')
        
        #,'product__type__category'
        #qs = qs.prefetch_related(models.Prefetch(''))
        #no use: 'product__type__category'
        #import pdb; pdb.set_trace() 



class OrderItemRemaingMethods():
    pass
    """
    @property
    @decorate(short_description = "print")
    def print_remain(self):
        if self.product.type.print:
            return self.quantity - self.print_total
        return '-'
    @property
    @decorate(short_description = "cut")
    def cut_remain(self):
        if self.product.type.cut:
            return self.quantity - self.cut_total
        return '-'
    # @property
    # @decorate(short_description = "sew")
    # def sew_remain(self):
    #     if self.product.type.sew:
    #         return self.quantity - self.sew_total
    #     return '-'
    @property
    @decorate(short_description = "weld")
    def weld_remain(self):
        if self.product.type.weld:
            return self.quantity - self.weld_total
        return '-'
    @property
    @decorate(short_description = "stuff")
    def stuff_remain(self):
        if self.product.type.stuff:
            return self.quantity - self.stuff_total
        return '-'
    @property
    @decorate(short_description = "pack")
    def pack_remain(self):
        if self.product.type.pack:
            return self.quantity - self.pack_total
        return '-'
    """



class OrderItemTotalSummaryMethods():
    ''' get the totals from sumtally for each process for the given orderitem, method = <process>_total'''
    # '-' to not show misleading zero for a product for which process does not exist
    # '-' logic is now twisted with downstream functions,  maybe redesign
    pass
    """
    @property
    @decorate(short_description = "Printed") # changed to distinguish in ops views
    def print_tallytotal(self):
        if self.product.type.print:
            # this is unique to print (to track locations of print)
            roll_data = get_roll_groups(self.tally_print)
            return roll_data[0] # todo find a way to display roll totals 
        return '-'
    @property
    @decorate(short_description = "Cut")
    def cut_tallytotal(self):
        if self.product.type.cut:
            return sumtally(self.tally_cut)
        return '-'
    @property
    @decorate(short_description = "Weld")
    def weld_tallytotal(self):
        if self.product.type.weld:
            return sumtally(self.tally_weld)
        return '-'
    @property
    @decorate(short_description = "Stuff")
    def stuff_tallytotal(self):
        if self.product.type.stuff:
            return sumtally(self.tally_stuff)
        return '-'
    @property
    @decorate(short_description = "Pack")
    def pack_tallytotal(self):
        if self.product.type.pack:
            return sumtally(self.tally_pack)
        return '-'
    """
    """
    @property 
    @decorate(short_description = "progress") 
    def item_progress(self): # todo -> move to annotation
        # needs more work
        total = 0
        count = 0
        for wf in self.work_fields:
            subtotal = getattr(self, wf+'_total')
            #if isinstance(subtotal, int):
            count+=1
            total += subtotal 
        if count:
            progress = total*100/count/self.quantity # %
        return round(progress,0) if count else '-'
    """
    # @property
    # def product_notes(self):
    #     return self.product.notes

#from class OrderItemRelatedModelMethods():
    #@property
    #def company(self):
    #    return self.order.company
    #@property
    #def order_notes(self):
    #    return '%s' % (self.order.notes)
    #@ property
    #def container(self):
    #    return self.order.container
    #@property
    #def DD(self):
    #    return self.order.container.dispatch_date
    #@property
    #def category(self):
    #    # not used
    #    return self.product.type.category.title
    #@property
    #def type(self):
    #   return self.product.type.title
  
    #@property
    #def qnotes(self):
    #    qq = [entry.note for entry in self.product.productnotes.all()] #qnote
    #    return qq

# model proxy junk


# --- Order ----------

"""
class OrderProxyManager(models.Manager):
    ''' optimize queries with prefetches and annotations, (reduces queries by 1 order of magnitude)'''
    #use_for_related_fields = True
    # def get_queryset(self):
    #     return OrderQuerySet(self.model, using=self._db)
    #import pdb; pdb.set_trace() 
    def get_queryset(self):
        qs =  super().get_queryset()
        
        # the following both work
        #qs = qs.all().annotate(qqq=models.Value('order all qqq annotation', output_field=models.CharField())) # testing
        #qs = qs.annotate(qprocess=models.Value('print', output_field=models.CharField()))
        #category_titles = ccc('{category}_remain_' + self.process)
        #self.totalsum_list = [w+'_totals' for w in self.category_titles]
        return qs

class OrderProxy2(Order):
    #objects =OrderProxyManager()
    class Meta:
        proxy = True
        #verbose_name_plural = 'Operations Order View'
"""



"""
class OrderItemPrint(OrderItemProxy):
    #process = 'print'
    class Meta:
        proxy = True
    # @property
    # @decorate(short_description = work_field_names_plural[self.process])
    # def total_html(self):
    #     return format_html('<b>{}</b>', getattr(self, self.process + '_total')) 

class OrderItemCut(OrderItemProxy):
    process = 'cut'
    class Meta:
        proxy = True
    # @property
    # @decorate(short_description = work_field_names_plural[process])
    # def total_html(self):
    #     return format_html('<b>{}</b>', getattr(self, self.process + '_total')) 
   

class OrderItemWeld(OrderItemProxy):
    process = 'weld'
    class Meta:
        proxy = True
    

class OrderItemStuff(OrderItemProxy):
    process = 'stuff'
    class Meta:
        proxy = True
  

class OrderItemPack(OrderItemProxy):
    process = 'pack'
    class Meta:
        proxy = True
   

class OrderItemOps(OrderItem):
    class Meta:
        proxy = True
    @property
    def progress(self):
        #return '{0:.0f}%'.format(self.item_progress) 
        color = '787878'
        # <small>
        return format_html('<span style="color: #{};">{}</span>', color, '{0:.0f}%'.format(self.item_progress))
    def __str__(self):
        return '%s of %s' % (self.quantity, self.product)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


"""

"""
class OrderOps(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Operations Order View'
    def __str__(self): # added only for experimenting with adding totals-row to list-view)
        if self.id:
            return '%s'% self.id
        else:
            return self.custom_alias_name
    # temporary
    process = 'all'
    category_titles = ccc('{category}_progress_all') # for ops
    totalsum_list = [w+'_totals' for w in category_titles] # crude hack implimented
   
  

class OrderPrint(Order):
    process = 'print'
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Print View'
    category_titles = ccc('{category}_remain_' + process)
    totalsum_list =  [w+'_totals' for w in category_titles]
    


class OrderCut(Order):
    process = 'cut'
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Cut View'


class OrderWeld(Order):
    process = 'weld'
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Weld View'



class OrderStuff(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Stuff View'

class OrderPack(Order):
    class Meta:
        proxy = True
        verbose_name_plural = 'Works Pack View'
"""


# from utils.py


"""
class TestDynamic(models.Model):
    test = models.BooleanField(default=False) 
    class Meta:
        #app_label = 'erp'
        pass
    def _test(self):
        return self.process


class AccessMixin():
    def get_related_field(name, admin_order_field=None, short_description=None):
        '''dynamic access to related model attributes, or query object annotations
            from admin list_display strings etc
            add <name>__html to get html markup contained in the annotation'''
        #@property
        html = None
        def _html(value):
            # obj.strip(')(').split(',') 
            html = mark_safe(value)
            #html = format_html('<span style="color: #{};">{}</span>', '008000', value)
            return html
        related_names = [x for x in name.split('__') if x]
        if related_names[-1] == 'html':
            html = related_names.pop() 
        if related_names[-1].startswith('@'):
            farg = related_names.pop()[1:]
        def dynamic_attribute(obj):
            for related_name in related_names:
                if 'ppp' in related_names:
                #import pdb; pdb.set_trace()
                    pass
                obj = getattr(obj, related_name) #()
            if farg:
                return obj(farg)
            return _html(obj) if html else mark_safe(obj) # with mark_safe on all no longer require html function
        dynamic_attribute.admin_order_field = admin_order_field or '__'.join(related_names) #name
        dynamic_attribute.short_description = short_description or related_names[-1].title().replace('_', ' ')
        return dynamic_attribute
    def __getattr__(self, attr):
        if '__' in attr:
            #import pdb; pdb.set_trace()
            return self.get_related_field(attr)
        # not dynamic lookup, default behaviour
        return self.__getattribute__(attr)
"""
