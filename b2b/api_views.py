import json
from django.http import HttpResponse
from b2b.models import *
from feedback.models import *
from django.core import serializers
from reversion import revisions as reversion
from django.db import transaction

from rest_framework import generics
from .serializers import *
from .models import Employee
from rest_framework import authentication, permissions


@transaction.atomic()
@reversion.create_revision()
def b_entity(request):
    response_data = {'result': '', 'message': ''}
    if request.method == "POST":
        data = json.loads(request.body)

        b_email = data['b_email']

        # Check if User Exists
        if User.objects.filter(email=b_email).exists():
            # Get b_entity from user email
            user = User.objects.get(email=b_email)
            incharge = Incharge.objects.get(user=user)
            b_entity = BEntity.objects.get(pk=incharge.b_entity.pk)
            employees = Employee.objects.filter(b_entity=b_entity.pk)
            pins = []
            for employee in employees:
                pins.append(employee.pin)
            data = {
                'qts': {
                    'qs1': 'AMBIENCE',
                    'qs2': 'COST',
                    'qs3': 'FOOD',
                    'qs4': 'SERVICE',
                    'qd1': b_entity.qd1_text,
                    'qd2': b_entity.qd2_text,
                },
                'pins': pins
            }
            return HttpResponse(json.dumps(data), content_type='application/json')

    response_data['result'] = 'error'
    response_data['message'] = 'Invalid Login !'
    return HttpResponse(json.dumps(response_data), content_type='application/json')


# BEntity List
class BEntityList(generics.ListCreateAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = BEntity.objects.all()
    serializer_class = BEntitySerializer


# Single BEntity
class BEntityDetail(generics.RetrieveAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = BEntity.objects.all()
    serializer_class = BEntitySerializer


# Single StatsBEntity
class StatsBEntityDetail(generics.RetrieveAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = StatsBEntity.objects.all()
    serializer_class = StatsBEntitySerializer
    lookup_field = 'b_entity'


# Employees List
class EmployeeList(generics.ListCreateAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        b_entity = self.kwargs['b_entity']
        return Employee.objects.filter(b_entity=b_entity)


# Single Employee
class EmployeeDetail(generics.RetrieveAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer





