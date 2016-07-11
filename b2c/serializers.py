from rest_framework import serializers
from .models import Customer
from registration.models import Address, Mobile


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('street', 'city', 'state', 'country',)


class MobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mobile
        fields = ('number',)


class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    mobile = MobileSerializer()

    class Meta:
        model = Customer
        fields = ('id', 'first_name', 'last_name', 'address', 'mobile',)
