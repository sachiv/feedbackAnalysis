from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from registration.models import UserProfileBase, Address, Mobile
from datetime import datetime


# Business Entity Model
class BEntity(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, default="Company")
    address = models.ForeignKey(Address, null=True, blank=True)
    mobile = models.ForeignKey(Mobile)
    fax = models.CharField(max_length=10, blank=True)
    email = models.EmailField(max_length=70, blank=True, null=True)
    qd1_text = models.CharField(max_length=100)
    qd2_text = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Incharge(models.Model):
    user = models.ForeignKey(User)
    b_entity = models.ForeignKey(BEntity)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name()


class Employee(UserProfileBase):
    b_entity = models.ForeignKey(BEntity)
    pin = models.CharField(max_length=4, blank=False, null=False, default='0000')

    def __str__(self):
        return self.get_full_name()


class QDBackupBase(models.Model):
    b_entity = models.ForeignKey(BEntity, null=False, blank=False)
    q_text = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.q_text

    class Meta:
        abstract = True


class QD1Backup(QDBackupBase):
    pass


class QD2Backup(QDBackupBase):
    pass


class AlertList(models.Model):
    b_entity = models.ForeignKey(BEntity, null=False, blank=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.ForeignKey(Mobile, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    nfa_sms = models.BooleanField(default=True, null=False, blank=False)
    nfa_email = models.BooleanField(default=True, null=False, blank=False)
    daily_report_sms = models.BooleanField(default=True, null=False, blank=False)
    daily_report_email = models.BooleanField(default=True, null=False, blank=False)
    archive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StatsBEntity(models.Model):
    b_entity = models.ForeignKey(BEntity)
    overall_rating = models.FloatField(null=False, blank=False, default=0)
    greys = models.IntegerField(null=False, blank=False, default=0)
    greens = models.IntegerField(null=False, blank=False, default=0)
    customers = models.IntegerField(null=False, blank=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.overall_rating)


class StatsBEntityDaily(models.Model):
    b_entity = models.ForeignKey(BEntity)
    greys = models.IntegerField(null=False, blank=False, default=0)
    greens = models.IntegerField(null=False, blank=False, default=0)
    date = models.DateField(null=False, blank=False, default=datetime.now().date())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.greys + self.greens)


class StatsBEntityHourly(models.Model):
    b_entity = models.ForeignKey(BEntity)
    date = models.DateField(null=False, blank=False, default=datetime.now().date())
    hour = models.IntegerField(null=False, blank=False)
    greys = models.IntegerField(null=False, blank=False, default=0)
    greens = models.IntegerField(null=False, blank=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.greys + self.greens)


class ReportsSent(models.Model):
    user = models.ForeignKey(User, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BEntityAccess(models.Model):
    user = models.ForeignKey(User)
    b_entity = models.ForeignKey(BEntity)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name()
