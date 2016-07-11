from __future__ import unicode_literals
from b2b.models import *
from b2c.models import Customer
from feedback.app_settings import RATING_CHOICES, DEFAULT_RATING_CHOICE, MAX_LENGTH_RATING_CHOICE
from datetime import timedelta
from django.utils.encoding import smart_unicode


class Feedback(models.Model):
    b_entity = models.ForeignKey(BEntity)
    incharge = models.ForeignKey(Incharge, blank=True, null=True)
    employee = models.ForeignKey(Employee)
    customer = models.ForeignKey(Customer)
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        msg = '%s FOR %s' % (self.customer.get_full_name(), self.b_entity.name)
        return msg.strip()

    def get_customer_number(self):
        return self.customer.mobile

    def get_qs1(self):
        try:
            q = float(QS1.objects.get(feedback=self).rating)
        except ValueError:
            q = float("0.5")
        return q

    def get_qs2(self):
        try:
            q = float(QS2.objects.get(feedback=self).rating)
        except ValueError:
            q = float("0.5")
        return q

    def get_qs3(self):
        try:
            q = float(QS3.objects.get(feedback=self).rating)
        except ValueError:
            q = float("0.5")
        return q

    def get_qs4(self):
        try:
            q = float(QS4.objects.get(feedback=self).rating)
        except ValueError:
            q = float("0.5")
        return q

    def get_qd1(self):
        try:
            q = float(QD1.objects.get(feedback=self).rating)
        except ValueError:
            q = float("0.5")
        return q

    def get_qd2(self):
        try:
            q = float(QD2.objects.get(feedback=self).rating)
        except Exception:
            q = float("0.5")
        return q

    def get_overall_rating(self):
        try:
            qs1 = float(QS1.objects.get(feedback=self).rating)
        except ValueError:
            qs1 = 0.5

        try:
            qs2 = float(QS2.objects.get(feedback=self).rating)
        except ValueError:
            qs2 = 0.5

        try:
            qs3 = float(QS3.objects.get(feedback=self).rating)
        except ValueError:
            qs3 = 0.5

        try:
            qs4 = float(QS4.objects.get(feedback=self).rating)
        except ValueError:
            qs4 = 0.5

        overall_rating = (qs1+qs2+qs3+qs4)/4
        return overall_rating

    def get_timestamp(self):
        return self.timestamp

    def if_green(self):
        if self.get_overall_rating() > 2 and self.get_qs3() > 2 and self.get_qs4() > 2:
            return True
        else:
            return False

    def get_comment(self):
        try:
            comment = smart_unicode(self.comment)
            self.comment = comment.encode('ascii', 'ignore')
            self.save()
        except Exception, e:
            comment = ''

        return comment

    def get_customer_first_name(self):
        try:
            first_name = smart_unicode(self.customer.first_name)
            self.customer.first_name = first_name.encode('ascii', 'ignore')
            self.customer.save()
        except Exception, e:
            first_name = ''

        return first_name

    def get_customer_last_name(self):
        try:
            last_name = smart_unicode(self.customer.last_name)
            self.customer.last_name = last_name.encode('ascii', 'ignore')
            self.customer.save()
        except Exception, e:
            last_name = ''

        return last_name

    get_qs1.short_description = 'QS1'
    get_qs2.short_description = 'QS2'
    get_qs3.short_description = 'QS3'
    get_qs4.short_description = 'QS4'
    get_qd1.short_description = 'QD1'
    get_qd2.short_description = 'QD2'
    get_overall_rating.short_description = 'Overall Rating'
    get_customer_number.short_description = 'Customer Mobile'
    get_timestamp.short_description = 'Timestamp'
    get_comment.short_description = 'Comment'
    get_customer_first_name.short_description = 'Customer First Name'
    get_customer_last_name.short_description = 'Customer Last Name'


class QuestionBase(models.Model):
    feedback = models.OneToOneField(Feedback)
    rating = models.CharField(
        choices=RATING_CHOICES, default=DEFAULT_RATING_CHOICE, max_length=MAX_LENGTH_RATING_CHOICE, null=False,
        blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.rating

    class Meta:
        abstract = True


class QS1(QuestionBase):
    pass


class QS2(QuestionBase):
    pass


class QS3(QuestionBase):
    pass


class QS4(QuestionBase):
    pass


class QD1(QuestionBase):
    pass


class QD2(QuestionBase):
    pass

