from rest_framework import generics
from .serializers import CustomerSerializer
from .models import Customer
from rest_framework import authentication, permissions


class CustomerList(generics.ListCreateAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

