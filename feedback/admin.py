from django.contrib import admin
from .models import *
from feedbackanalysis.util import export_as_csv_action
from reversion.admin import VersionAdmin


class QS1Inline(admin.TabularInline):
    model = QS1


class QS2Inline(admin.TabularInline):
    model = QS2


class QS3Inline(admin.TabularInline):
    model = QS3


class QS4Inline(admin.TabularInline):
    model = QS4


class QD1Inline(admin.TabularInline):
    model = QD1


class QD2Inline(admin.TabularInline):
    model = QD2


class FeedbackAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ('pk', 'b_entity', 'incharge', 'employee', 'get_customer_first_name', 'get_customer_number',
                    'get_qs1', 'get_qs2', 'get_qs3', 'get_qs4', 'get_qd1', 'get_qd2', 'get_overall_rating',
                    'get_comment', 'get_timestamp',)
    list_filter = ('b_entity',)
    actions = [export_as_csv_action("CSV Export")]
    inlines = [QS1Inline, QS2Inline, QS3Inline, QS4Inline, QD1Inline, QD2Inline, ]


admin.site.register(Feedback, FeedbackAdmin)
