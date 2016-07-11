from rest_framework import serializers
from .models import *
from registration.models import Address, Mobile


class BEntityNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BEntity
        fields = ('id', 'name',)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('street', 'city', 'state', 'country',)


class MobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mobile
        fields = ('number',)


class StatsBEntitySerializer(serializers.ModelSerializer):

    class Meta:
        model = StatsBEntity
        fields = ('overall_rating', 'greys', 'greens', 'customers',)


class BEntitySerializer(serializers.ModelSerializer):
    mobile = MobileSerializer()
    address = AddressSerializer()

    class Meta:
        model = BEntity
        fields = ('id', 'name', 'mobile', 'email', 'address', 'fax', 'qd1_text', 'qd2_text')


class EmployeeSerializer(serializers.ModelSerializer):
    b_entity = BEntityNameSerializer()
    mobile = MobileSerializer()
    address = AddressSerializer()

    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'email', 'mobile', 'fax', 'address', 'age', 'b_entity', 'pin',)
