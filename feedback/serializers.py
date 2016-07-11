from rest_framework import serializers
from .models import *
from b2b.models import BEntity, Incharge, Employee
from django.contrib.auth.models import User
from registration.models import Address, Mobile


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name',)


class InchargeNameSerializer(serializers.ModelSerializer):
    user = UserNameSerializer()

    class Meta:
        model = Incharge
        fields = ('id', 'user',)


class BEntityNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BEntity
        fields = ('id', 'name',)


class EmployeeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'pin')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('street', 'city', 'state', 'country',)


class MobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mobile
        fields = ('number',)


class FeedbackSerializer(serializers.ModelSerializer):
    b_entity = BEntityNameSerializer()
    employee = EmployeeNameSerializer()
    incharge = InchargeNameSerializer()

    class Meta:
        model = Feedback
        fields = ('id', 'b_entity', 'incharge', 'employee', 'comment', 'get_qs1', 'get_qs2', 'get_qs3', 'get_qs4',
                  'get_qd1', 'get_qd2', 'timestamp')
