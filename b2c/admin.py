from django.contrib import admin
from .models import *
from feedbackanalysis.util import export_as_csv_action
from reversion.admin import VersionAdmin


class CustomerAdmin(VersionAdmin):
    list_display = ('pk', 'get_name', 'mobile', 'email', 'dt_bday', 'dt_anni')
    search_fields = ['first_name', 'last_name', 'mobile']
    actions = [export_as_csv_action("CSV Export")]

    def get_name(self, obj):
        return obj.get_full_name()

    get_name.short_description = 'Name'

    pass

admin.site.register(Customer, CustomerAdmin)
