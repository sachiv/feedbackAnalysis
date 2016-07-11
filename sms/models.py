from django.db import models
from b2b.models import BEntity, Incharge
from shop.models import AssetAccount
from django.contrib.auth.models import User


class PromoSMS(models.Model):
    PERSONAL, COMMON = 'PERSONAL', 'COMMON'
    TEMPLATE_TYPE = ((PERSONAL, 'PERSONAL'), (COMMON, 'COMMON'))

    b_entity = models.ForeignKey(BEntity, null=True, default=0, blank=True)
    title = models.CharField(max_length=100, null=False, blank=False)
    content = models.TextField(null=False, blank=False)
    type = models.CharField(max_length=50, choices=TEMPLATE_TYPE, null=False, default=PERSONAL)
    active = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PromoSMSStats(models.Model):
    user = models.ForeignKey(User, null=False, blank=False)
    promo_sms = models.ForeignKey(PromoSMS, null=False, blank=False)
    nb_sms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.promo_sms.title


class SMSAccountBase(models.Model):
    asset_account = models.ForeignKey(AssetAccount, null=False, blank=False)
    loginid = models.CharField(max_length=100, null=False, blank=False)
    password = models.CharField(max_length=100, null=False, blank=False)
    active = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.asset_account)

    class Meta:
        abstract = True


class SMSAccount(SMSAccountBase):
    pass


class SMSAccountTrans(SMSAccountBase):
    pass








