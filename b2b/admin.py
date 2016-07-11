from django.contrib import admin
from .models import *
from feedbackanalysis.util import export_as_csv_action
from reversion.admin import VersionAdmin
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.core.urlresolvers import reverse


class BEntityAccessInline(admin.TabularInline):
    model = BEntityAccess


class BEntityAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ('pk', 'name', 'mobile', 'email', 'qd1_text', 'qd2_text')
    list_filter = ('qd1_text', 'qd2_text',)
    search_fields = ['name', 'mobile', 'email']
    actions = [export_as_csv_action("CSV Export")]
    inlines = [BEntityAccessInline, ]
    pass


class InchargeAdmin(VersionAdmin):
    list_display = ('pk', 'get_user_name', 'get_user_email', 'b_entity', )
    list_filter = ('b_entity',)
    search_fields = ['b_entity']
    actions = [export_as_csv_action("CSV Export")]

    def get_user_name(self, obj):
        return obj.user.get_full_name()
    get_user_name.short_description = 'Name'

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'

    pass


class EmployeeAdmin(VersionAdmin):
    list_display = ('pk', 'get_name', 'b_entity', 'pin', 'mobile')
    list_filter = ('b_entity',)
    search_fields = ['first_name', 'last_name', 'b_entity', 'pin']
    actions = [export_as_csv_action("CSV Export")]

    def get_name(self, obj):
        return obj.get_full_name()
    get_name.short_description = 'Name'

    pass


class QD1BackupAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ('b_entity', 'q_text')
    list_filter = ('b_entity',)
    search_fields = ['q_text', 'b_entity']
    actions = [export_as_csv_action("CSV Export")]
    pass


class QD2BackupAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ('b_entity', 'q_text')
    list_filter = ('b_entity',)
    search_fields = ['q_text', 'b_entity']
    actions = [export_as_csv_action("CSV Export")]
    pass


class AlertListAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ('b_entity', 'name', 'mobile', 'email', 'nfa_sms', 'nfa_email', 'daily_report_sms',
                    'daily_report_email', 'archive')
    list_filter = ('b_entity', 'mobile', 'email', 'nfa_sms', 'nfa_email', 'daily_report_sms',
                   'daily_report_email', 'archive')
    search_fields = ['b_entity', 'name', 'mobile', 'email', 'nfa_sms', 'nfa_email', 'daily_report_sms',
                     'daily_report_email', 'archive']
    actions = [export_as_csv_action("CSV Export")]
    pass


class StatsBEntityAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ('b_entity', 'overall_rating', 'greys', 'greens', 'customers')
    list_filter = ('b_entity',)
    search_fields = ['customers', 'b_entity']
    actions = [export_as_csv_action("CSV Export")]
    pass


class StatsBEntityDailyAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ('b_entity', 'greys', 'greens', 'date')
    list_filter = ('b_entity',)
    search_fields = ['b_entity']
    actions = [export_as_csv_action("CSV Export")]
    pass


class StatsBEntityHourlyAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ('b_entity', 'date', 'hour', 'greys', 'greens', 'created_at', 'updated_at')
    list_filter = ('b_entity', 'date', 'hour')
    search_fields = ['b_entity', 'date', 'hour']
    actions = [export_as_csv_action("CSV Export")]
    pass


class ReportsSent(VersionAdmin, admin.ModelAdmin):
    list_display = ('user', 'date', 'created_at', 'updated_at')
    list_filter = ('user',)
    search_fields = ['b_entity']
    actions = [export_as_csv_action("CSV Export")]
    pass


class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'

    readonly_fields = LogEntry._meta.get_all_field_names()

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = u'<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return link

    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'

    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')


admin.site.register(BEntity, BEntityAdmin)
admin.site.register(Incharge, InchargeAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(QD1Backup, QD1BackupAdmin)
admin.site.register(QD2Backup, QD2BackupAdmin)
admin.site.register(AlertList, AlertListAdmin)
admin.site.register(StatsBEntity, StatsBEntityAdmin)
admin.site.register(StatsBEntityDaily, StatsBEntityDailyAdmin)
admin.site.register(StatsBEntityHourly, StatsBEntityHourlyAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
