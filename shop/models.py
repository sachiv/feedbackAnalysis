from django.db import models
from django.contrib.auth.models import User
from feedbackanalysis.util import generate_smart_id
from django.db import IntegrityError
from treebeard.mp_tree import MP_Node
from django.utils.encoding import python_2_unicode_compatible
from b2b.models import BEntity
from datetime import datetime
from django.shortcuts import get_object_or_404

@python_2_unicode_compatible
class ProductCategory(MP_Node):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)

    node_order_by = ['name']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        names = [a.name for a in self.get_ancestors()]
        names.append(self.name)
        return " > ".join(names)


class Product(models.Model):
    product_id = models.CharField(max_length=15, blank=True, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    category = models.ForeignKey(ProductCategory, null=False)
    stock = models.IntegerField(default=0)
    validity = models.BigIntegerField(default=0, null=True, blank=True)
    unit = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    unlimited_stock = models.BooleanField(default=True)
    unlimited_validity = models.BooleanField(default=True)
    unlimited_unit = models.BooleanField(default=True)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = generate_smart_id(15)
        success = False
        failures = 0
        while not success:
            try:
                super(Product, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if failures > 5:
                    raise
                else:
                    self.product_id = generate_smart_id(15)
            else:
                success = True


class ProductOption(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductAddOn(models.Model):
    product = models.ForeignKey(Product, null=False)
    option = models.ForeignKey(ProductOption, null=False)
    price_add = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        string = self.option.name + " for " + self.product.name
        return string


class PackageProduct(models.Model):
    package = models.ForeignKey(Product, null=False, related_name="package")
    product = models.ForeignKey(Product, null=False, related_name="product")
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        string = str(self.product) + " for " + str(self.package)
        return string


class Coupon(models.Model):
    code = models.CharField(max_length=50, null=False)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True)
    validity = models.BigIntegerField(default=0, null=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    offer = models.TextField(null=False)
    condition = models.TextField(null=False)

    def __str__(self):
        return self.code


class BalanceAccount(models.Model):
    OPEN, FROZEN, CLOSED = 'OPEN', 'FROZEN', 'CLOSED'
    ACCOUNT_STATUS = ((OPEN, 'OPEN'), (FROZEN, 'FROZEN'), (CLOSED, 'CLOSED'),)

    account_id = models.CharField(max_length=10, blank=True, editable=False, unique=True, db_index=True)
    balance = models.FloatField(default=0, null=False, blank=False)
    credit_limit = models.FloatField(null=True, blank=True, default=0)
    status = models.CharField(max_length=50, choices=ACCOUNT_STATUS, null=False, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.account_id:
            self.account_id = generate_smart_id(10)
        success = False
        failures = 0
        while not success:
            try:
                super(BalanceAccount, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if failures > 5:
                    raise
                else:
                    self.account_id = generate_smart_id(10)
            else:
                success = True

    def __str__(self):
        bentity = get_object_or_404(BalanceAccountHolder, balance_account=self).b_entity
        return bentity.name


class BalanceAccountHolder(models.Model):
    b_entity = models.ForeignKey(BEntity, blank=False, null=False)
    balance_account = models.ForeignKey(BalanceAccount, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.balance_account) + " of " + str(self.b_entity)


class AssetAccount(models.Model):
    balance_account = models.OneToOneField(BalanceAccount)
    sms_promo = models.IntegerField(default=0, null=True, blank=True)
    sms_promo_validity = models.DateTimeField(null=False, blank=False, default=datetime.now)
    sms_nfa_validity = models.DateTimeField(null=False, blank=False, default=datetime.now)
    sms_thankyou_validity = models.DateTimeField(null=False, blank=False, default=datetime.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.balance_account)


class Transaction(models.Model):
    INITIATED, PROCESSING, PENDING, SUCCESS, FAILED = 'INITIATED', 'PROCESSING', 'PENDING', 'SUCCESS', 'FAILED'
    TRANSACTION_STATUS = ((INITIATED, 'INITIATED'), (PROCESSING, 'PROCESSING'), (PENDING, 'PENDING'),
                          (SUCCESS, 'SUCCESS'), (FAILED, 'FAILED'))

    RECHARGE, TRANSFER, ORDER = 'RECHARGE', 'TRANSFER', 'ORDER'
    TRANSACTION_TYPE = ((RECHARGE, 'RECHARGE'), (TRANSFER, 'TRANSFER'), (ORDER, 'ORDER'))

    transaction_id = models.CharField(max_length=20, blank=True, editable=False, unique=True, db_index=True)
    amount = models.FloatField(default=0, null=False)
    type = models.CharField(max_length=50, choices=TRANSACTION_TYPE, null=False, default=ORDER)
    status = models.CharField(max_length=50, choices=TRANSACTION_STATUS, null=False, default=FAILED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = generate_smart_id(20)
        success = False
        failures = 0
        while not success:
            try:
                super(Transaction, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if failures > 5:
                    raise
                else:
                    self.transaction_id = generate_smart_id(20)
            else:
                success = True

    def __str__(self):
        return self.transaction_id


class Order(models.Model):
    order_id = models.CharField(max_length=16, blank=True, editable=False, unique=True, db_index=True)
    transaction = models.ForeignKey(Transaction, null=False, default=0)
    account = models.ForeignKey(BalanceAccount, null=False)
    ordered_by = models.ForeignKey(User, null=False)
    amount = models.FloatField(default=0)
    coupon_applied = models.ForeignKey(Coupon, null=True)
    discount = models.FloatField(default=0)
    payed = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = generate_smart_id(16)
        success = False
        failures = 0
        while not success:
            try:
                super(Order, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if failures > 5:  # or some other arbitrary cutoff point at which things are clearly wrong
                    raise
                else:
                    # looks like a collision, try another random value
                    self.order_id = generate_smart_id(16)
            else:
                success = True

    def __str__(self):
        return self.order_id


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, null=False)
    product = models.ForeignKey(Product, null=False)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        string = str(self.product) + " for " + str(self.order)
        return string


class Recharge(models.Model):
    CASH = 'CASH'
    PAYMENT_MODE = ((CASH, 'CASH'),)

    transaction = models.ForeignKey(Transaction, null=False)
    amount = models.FloatField(default=0, null=False)
    receipt_nb = models.CharField(max_length=20, null=True, blank=True)
    destination = models.ForeignKey(BalanceAccount, null=False)
    staff = models.ForeignKey(User, limit_choices_to={'is_staff': True}, null=False)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE, null=False, default=CASH)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.receipt_nb


class Transfer(models.Model):
    transaction = models.ForeignKey(Transaction, null=False)
    amount = models.FloatField(default=0, null=False)
    source = models.ForeignKey(BalanceAccount, null=False, related_name='transfer_source')
    destination = models.ForeignKey(BalanceAccount, null=False, related_name='transfer_destination')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.source + " " + self.destination








