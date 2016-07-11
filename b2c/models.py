from __future__ import unicode_literals
from registration.models import UserProfileBase
from django.db import models


class Customer(UserProfileBase):
    dt_bday = models.DateField(blank=True, null=True)
    dt_anni = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.get_full_name()
