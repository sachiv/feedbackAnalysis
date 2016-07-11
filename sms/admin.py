from django.contrib import admin
from .models import *
from feedbackanalysis.util import export_as_csv_action
from reversion.admin import VersionAdmin


class PromoSMSAdmin(VersionAdmin):
    list_display = ('b_entity', 'title', 'content', 'active', 'archive')
    list_filter = ('b_entity', 'active', 'archive',)
    search_fields = ['title', 'b_entity']
    actions = [export_as_csv_action("CSV Export")]

    pass


class PromoSMSStatsAdmin(VersionAdmin):
    list_display = ('user', 'promo_sms', 'nb_sms', 'created_at', 'updated_at')
    list_filter = ('user', 'promo_sms',)
    search_fields = ['promo_sms', 'user']
    actions = [export_as_csv_action("CSV Export")]

    pass


class SMSAccountAdmin(VersionAdmin):
    list_display = ('asset_account', 'loginid', 'password', 'active', 'archive',)
    list_filter = ('active', 'archive',)
    search_fields = ['assets_account', 'title']
    actions = [export_as_csv_action("CSV Export")]

    pass

admin.site.register(PromoSMS, PromoSMSAdmin)
admin.site.register(PromoSMSStats, PromoSMSStatsAdmin)
admin.site.register(SMSAccount, SMSAccountAdmin)
admin.site.register(SMSAccountTrans, SMSAccountAdmin)
