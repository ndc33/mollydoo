from django import forms
from django.db import models
#from django.db.models import Q, F, Count
from django.contrib import admin
#from django.urls import reverse
#from django.utils.html import format_html
#from django.utils.safestring import mark_safe
#from django.contrib.auth.models import User, Group
#from django.contrib.admin.options import change_view
#from django.shortcuts import redirect

#from import_export import resources
#from import_export.admin import ImportExportModelAdmin, ImportExportMixin

#from ..models import Address, Company, Contact, Product, Order
from ..models import SpecNote
#from .setup import product_link

from .setup import erp_admin, site_proxy, name_proxy
#from .setup import text_box
from .workstemplate import admin2


@admin.register(SpecNote, site=site_proxy)
class ContactAdmin(admin2):
    remove_pk_controls = ['company','product','type','order']