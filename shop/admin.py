from django.contrib import admin
from .models import *
from feedbackanalysis.util import export_as_csv_action
from reversion.admin import VersionAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory


class PackageProductInline(admin.TabularInline):
    model = PackageProduct
    fk_name = 'package'
    extra = 1


class ProductCategoryAdmin(TreeAdmin):
    form = movenodeform_factory(ProductCategory)
    list_display = ('name',)
    actions = [export_as_csv_action("CSV Export")]

    pass


class ProductAdmin(VersionAdmin):
    list_display = ('product_id', 'name', 'price', 'category', 'stock', 'active', 'unlimited_stock',
                    'unlimited_validity')
    list_filter = ('category',)
    search_fields = ['name']
    actions = [export_as_csv_action("CSV Export")]
    inlines = [PackageProductInline, ]

    pass


class ProductOptionAdmin(VersionAdmin):
    list_display = ('name',)
    search_fields = ['name']
    actions = [export_as_csv_action("CSV Export")]

    pass


class ProductAddOnAdmin(VersionAdmin):
    list_display = ('product', 'option', 'price_add')
    list_filter = ('product', 'option')
    search_fields = ['product', 'option']
    actions = [export_as_csv_action("CSV Export")]

    pass


class CouponAdmin(VersionAdmin):
    list_display = ('code', 'title', 'active')
    search_fields = ['code']
    actions = [export_as_csv_action("CSV Export")]

    pass


class OrderProductInline(admin.TabularInline):
    model = OrderProduct


class OrderAdmin(VersionAdmin):
    list_display = ('order_id', 'transaction', 'account', 'ordered_by', 'amount',)
    list_filter = ('order_id', 'account', 'ordered_by',)
    search_fields = ['order_id', 'account', 'ordered_by']
    inlines = [OrderProductInline]
    actions = [export_as_csv_action("CSV Export")]

    pass


class BalanceAccountAdmin(VersionAdmin):
    list_display = ('account_id', 'status', 'balance', 'credit_limit',)
    list_filter = ('status', 'credit_limit',)
    search_fields = ['account_id', 'name']
    actions = [export_as_csv_action("CSV Export")]

    pass


class BalanceAccountHolderAdmin(VersionAdmin):
    list_display = ('b_entity', 'balance_account',)
    list_filter = ('b_entity', 'balance_account',)
    search_fields = ['b_entity', 'balance_account']
    actions = [export_as_csv_action("CSV Export")]

    pass


class AssetAccountAdmin(VersionAdmin):
    list_display = ('balance_account', 'sms_promo', 'sms_promo_validity', 'sms_nfa_validity', 'sms_thankyou_validity',)
    search_fields = ['balance_account', 'sms_promo']
    actions = [export_as_csv_action("CSV Export")]

    pass


class TransactionAdmin(VersionAdmin):
    list_display = ('transaction_id', 'amount', 'type', 'status', 'created_at', 'updated_at',)
    list_filter = ('status',)
    search_fields = ['transaction_id', 'amount']
    actions = [export_as_csv_action("CSV Export")]

    pass


class RechargeAdmin(VersionAdmin):
    list_display = ('transaction', 'amount', 'receipt_nb', 'destination', 'staff', 'payment_mode',
                    'created_at', 'updated_at',)
    list_filter = ('destination', 'staff', 'payment_mode')
    search_fields = ['transaction', 'amount', 'receipt_nb', 'destination', 'staff', 'payment_mode']
    actions = [export_as_csv_action("CSV Export")]

    pass


class TransferAdmin(VersionAdmin):
    list_display = ('transaction', 'amount', 'source', 'destination', 'created_at', 'updated_at',)
    list_filter = ('source', 'destination',)
    search_fields = ['transaction', 'amount', 'source', 'destination']
    actions = [export_as_csv_action("CSV Export")]

    pass


admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductOption, ProductOptionAdmin)
admin.site.register(ProductAddOn, ProductAddOnAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(BalanceAccount, BalanceAccountAdmin)
admin.site.register(BalanceAccountHolder, BalanceAccountHolderAdmin)
admin.site.register(AssetAccount, AssetAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Recharge, RechargeAdmin)
admin.site.register(Transfer, TransferAdmin)
