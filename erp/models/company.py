from django.db import models
from django.utils.html import format_html
import datetime

# used to access Product without circular references 
# no import, object use on access
# used to access 'Products'
import erp  
#from django.apps import apps # no benefits compared to app import

from ..utils import work_field_names

# TODO
# the present assosiation of addresses with companies is a mess, exploration of having multiple delivery addresses for
#   the same invoice entity -> we serve trade who drop ship to trade. Popular FK-to-self design appears useless. Ongoing
# simple-history not so impressive, may expore django reversion


class Address(models.Model):
    INVOICE =          'INVOICE'
    DELIVERY =         'DELIVERY'

    TYPE_CHOICES = (
        (INVOICE, 'Invoice'),
        (DELIVERY, 'Delivery'),
    )
    #  limit_choices_to={'is_staff': True} # example
    company = models.ForeignKey('COMPANY', related_name='addresses', on_delete=models.PROTECT)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=INVOICE)
    name = models.CharField(max_length=100)#, blank=True, default='') 
    address = models.TextField() 
    postcode = models.CharField(max_length=9)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    #history = HistoricalRecords(excluded_fields=['created_at','modified']) # keep example
    class Meta:
        verbose_name_plural = 'Addresses'
        # constraints = [ # can have multiple delivery addresses!
        # models.UniqueConstraint(fields=['company', 'type'], name='unique_address')
        # ]
    def __str__(self):
        return self.name


class Company(models.Model):
#class Place(PolymorphicModel):
    CUSTOMER = 'Customer'
    SUPPLIER = 'Supplier'
    OTHER =    'Other'

    ACTIVE =    'Active'
    LEAD =      'Lead'
    ARCHIVED =  'Archived'

    COMPANY_TYPE = (
        (CUSTOMER, 'Customer'),
        (SUPPLIER, 'Supplier'),
        (OTHER, 'Other')
    )

    COMPANY_STATUS = (
        (ACTIVE, 'Active'),
        (LEAD, 'Lead'),
        (ARCHIVED, 'Archived')
    )

    name = models.CharField(max_length=100, unique = True)
    shortname = models.CharField(max_length=20)#, unique = True)
    codename = models.CharField(max_length=4)#, unique = True, null=True)
    type = models.CharField(max_length=20, choices=COMPANY_TYPE, default=CUSTOMER)
    status = models.CharField(max_length=20, choices=COMPANY_STATUS, default=ACTIVE)
    VAT_Number = models.CharField(max_length=40, blank=True, default='')
    tax_status = models.CharField(max_length=100, blank=True, default='') # possible add choices
    office_notes = models.TextField(blank=True, default='')
    order_notes = models.TextField(blank=True, default='')
    manufacture_notes = models.TextField(blank=True, default='')
    delivery_notes = models.TextField(blank=True, default='')    
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    # ...
    @property
    def own_products(self):
        # how to avoid circular imports!
        qs = erp.admin.Products.objects.filter(company__pk = self.pk) # to test
        #alternsative: qs = apps.get_model('erp', 'Product').objects.filter(company__pk = self.pk) # Product.
        return qs
    #objects = InheritanceManager()
    class Meta:
        verbose_name_plural = 'Companies'
    def __str__(self):
        return self.name
   


class Contact(models.Model):
    company = models.ForeignKey(Company, related_name='contacts', on_delete=models.PROTECT)
    name = models.CharField(max_length=60)
    role = models.CharField(max_length=60)
    mobile_number = models.CharField(max_length=20, blank=True, default='')
    office_number = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(max_length=60, blank=True, default='')
    contact_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('company','name')
        constraints = [
        models.UniqueConstraint(fields=['company', 'name'], name='unique_contact')
        ]
    def __str__(self):
        return self.name
    # ...