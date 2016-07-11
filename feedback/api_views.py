import json
from django.http import HttpResponse
from shop.models import BalanceAccountHolder, AssetAccount
from sms.models import SMSAccountTrans
from feedback.models import *
from sms.util import send_message, send_message_trans
from reversion import revisions as reversion
from django.db import transaction
from datetime import datetime, timedelta
from feedbackanalysis.util import urlquote
from django.utils.dateparse import parse_datetime, parse_date
from django.utils import timezone

from rest_framework import generics
from .serializers import *
from .models import Feedback
from rest_framework import authentication, permissions


@transaction.atomic()
@reversion.create_revision()
def feedback(request):
    response_data = {'result': '', 'message': ''}
    if request.method == "POST":
        b_entity = None
        asset_account = None
        balance_account = None
        sms_account_trans = None
        employee = None
        data = json.loads(request.body)
        b_email = data['b_email']

        # Check if User Exists
        if User.objects.filter(email=b_email).exists():
            # Get b_entity from user email
            user = User.objects.filter(email=b_email)[0]
            incharge = Incharge.objects.get(user=user)
            b_entity = BEntity.objects.get(pk=incharge.b_entity.pk)
            if BalanceAccountHolder.objects.filter(b_entity=b_entity).exists():
                balance_account = BalanceAccountHolder.objects.get(b_entity=b_entity).balance_account
                if AssetAccount.objects.filter(balance_account=balance_account).exists():
                    asset_account = AssetAccount.objects.get(balance_account=balance_account)
                    if SMSAccountTrans.objects.filter(asset_account=asset_account).exists():
                        sms_account_trans = SMSAccountTrans.objects.get(asset_account=asset_account)
        else:
            response_data['result'] = 'error'
            response_data['message'] = 'Invalid Login !'
            return HttpResponse(json.dumps(response_data), content_type='application/json')

        pin = data['pin']
        if data['comment'] == "null":
            comment = ""
        else:
            comment = smart_unicode(data['comment']).encode('ascii', 'ignore')

        customer = data['customer']
        c_name = smart_unicode(customer['name']).encode('ascii', 'ignore')
        c_mobile = smart_unicode(customer['mobile']).encode('ascii', 'ignore')
        c_email = smart_unicode(customer['email']).encode('ascii', 'ignore')

        if 'timestamp' in data:
            try:
                timestamp = parse_datetime(data['timestamp']) + timedelta(hours=5, minutes=30)
            except Exception:
                timestamp = datetime.now() + timedelta(hours=5, minutes=30)
        else:
            timestamp = datetime.now() + timedelta(hours=5, minutes=30)

        if 'bday' in customer:
            dt_bday = parse_date(customer['bday'])
            print dt_bday
        else:
            dt_bday = None

        if 'anni' in customer:
            dt_anni = parse_date(customer['anni'])
        else:
            dt_anni = None

        ans = data['ans']

        # Check if Employee Exists
        if Employee.objects.filter(b_entity=b_entity, pin=pin).exists():
            employee = Employee.objects.get(b_entity=b_entity, pin=pin)
        else:
            response_data['result'] = 'error'
            response_data['message'] = 'Employee does not exist'
            return HttpResponse(json.dumps(response_data), content_type='application/json')

        # Check if Mobile Exists
        if Mobile.objects.filter(number=c_mobile).exists():
            c_mobile = Mobile.objects.filter(number=c_mobile)[0]
        else:
            try:
                c_mobile = Mobile.objects.create(number=c_mobile)
            except Exception:
                response_data['result'] = 'error'
                response_data['message'] = 'Invalid Mobile Number'
                return HttpResponse(json.dumps(response_data), content_type='application/json')

        # Check if Customer Exists
        new_customers = 0
        if Customer.objects.filter(mobile=c_mobile).exists():
            customer = Customer.objects.filter(mobile=c_mobile)[0]
            customer.first_name = c_name
            customer.email = c_mobile
            customer.email = c_email
            customer.dt_bday = dt_bday
            customer.dt_anni = dt_anni
            customer.save()
        else:
            try:
                customer = Customer.objects.create(first_name=c_name, mobile=c_mobile, email=c_email)
                customer.dt_bday = dt_bday
                customer.dt_anni = dt_anni
                customer.save()
                new_customers += 1
            except Exception:
                response_data['result'] = 'error'
                response_data['message'] = 'Invalid Customer Details'
                return HttpResponse(json.dumps(response_data), content_type='application/json')

        # Create Feedback
        try:
            feedback = Feedback.objects.create(b_entity=b_entity, incharge=incharge, employee=employee,
                                               customer=customer,
                                               comment=comment, timestamp=timestamp)
        except Exception:
            response_data['result'] = 'error'
            response_data['message'] = 'Invalid Feedback Details'
            return HttpResponse(json.dumps(response_data), content_type='application/json')

        # Check for null values
        if ans["qs1"] in [None, '', 'null']:
            ans["qs1"] = '0.5'
        if ans["qs2"] in [None, '', 'null']:
            ans["qs2"] = '0.5'
        if ans["qs3"] in [None, '', 'null']:
            ans["qs3"] = '0.5'
        if ans["qs4"] in [None, '', 'null']:
            ans["qs4"] = '0.5'
        if ans["qd1"] in [None, '', 'null']:
            ans["qd1"] = '0.5'
        if ans["qd2"] in [None, '', 'null']:
            ans["qd2"] = '0.5'

        # Create ratings
        QS1.objects.create(feedback=feedback, rating=ans["qs1"])
        QS2.objects.create(feedback=feedback, rating=ans["qs2"])
        QS3.objects.create(feedback=feedback, rating=ans["qs3"])
        QS4.objects.create(feedback=feedback, rating=ans["qs4"])
        QD1.objects.create(feedback=feedback, rating=ans["qd1"])
        QD2.objects.create(feedback=feedback, rating=ans["qd2"])

        overall_rating = feedback.get_overall_rating()

        # Send Thank You Message to Customer
        if asset_account.sms_thankyou_validity >= (timezone.now() + timedelta(hours=5, minutes=30)):
            mobiles_list = list()
            message = urlquote('Dear Customer,\n'+
                               'Thank you for giving your valuable feedback,\n'+
                               'Your opinion will really help us to improve further.\n'+
                               'From: '+b_entity.name+',\n Thank You')
            mobiles_list.append(str(c_mobile))
            if balance_account:
                if asset_account:
                    if sms_account_trans:
                        send_message_trans(sms_account_trans.loginid, sms_account_trans.password, mobiles_list, message)
                    else:
                        send_message(mobiles_list, message)
                else:
                    send_message(mobiles_list, message)
            else:
                send_message(mobiles_list, message)

        qs3 = float(ans["qs3"])
        qs4 = float(ans["qs4"])
        f_nb_greys = 0
        f_nb_greens = 0
        mobile_list = list()
        if overall_rating <= 2 or qs3 <= 2 or qs4 <= 2:
            if asset_account.sms_nfa_validity >= (timezone.now() + timedelta(hours=5, minutes=30)):
                # Send Negative Feedback SMS to B Entity
                message = urlquote('Dear Business Partner,You got a negative feedback\n' +
                                   'From\n' +
                                   customer.get_full_name() + ',\n' +
                                   customer.mobile.number + ',\n' +
                                   'Rating ' + str(overall_rating) + '/5,\n' +
                                   'Store- ' + b_entity.name + ',\n' +
                                   '"' + comment + '"')

                mobile_list.append(str(b_entity.mobile))
                if AlertList.objects.filter(b_entity=b_entity).exists:
                    nfa_list = A.objects.filter(b_entity=b_entity, archive=False)
                    for nfa_mobile in nfa_list:
                        mobile_list.append(str(nfa_mobile.mobile))
                send_message(mobile_list, message)
            f_nb_greys += 1
        else:
            f_nb_greens += 1

        # Update stats
        if not StatsBEntity.objects.filter(b_entity=b_entity).exists():
            # Creating new Stats Object
            today = datetime.now() + timedelta(hours=5, minutes=30)
            today_date = today.date()
            overall_rating = 0
            nb_feedbacks = 0
            nb_greys = 0
            nb_greens = 0
            nb_feedbacks_today = 0
            nb_greys_today = 0
            nb_greens_today = 0
            feedback_list = Feedback.objects.filter(b_entity=incharge.b_entity).order_by('-timestamp')
            customers = Feedback.objects.filter(b_entity=incharge.b_entity).values('customer').distinct()
            nb_customers = len(customers)
            for feedback in feedback_list:
                nb_feedbacks += 1
                qs1 = QS1.objects.get(feedback=feedback).rating
                qs2 = QS2.objects.get(feedback=feedback).rating
                qs3 = QS3.objects.get(feedback=feedback).rating
                qs4 = QS4.objects.get(feedback=feedback).rating
                qd1 = QD1.objects.get(feedback=feedback).rating
                qd2 = QD2.objects.get(feedback=feedback).rating

                if qs1 in [None, '', 'null']:
                    qs1 = '0.5'
                    q = QS1.objects.get(feedback=feedback)
                    q.rating = qs1
                    q.save()
                if qs2 in [None, '', 'null']:
                    qs2 = '0.5'
                    q = QS2.objects.get(feedback=feedback)
                    q.rating = qs2
                    q.save()
                if qs3 in [None, '', 'null']:
                    qs3 = '0.5'
                    q = QS3.objects.get(feedback=feedback)
                    q.rating = qs3
                    q.save()
                if qs4 in [None, '', 'null']:
                    qs4 = '0.5'
                    q = QS4.objects.get(feedback=feedback)
                    q.rating = qs4
                    q.save()
                if qd1 in [None, '', 'null']:
                    qd1 = '0.5'
                    q = QD1.objects.get(feedback=feedback)
                    q.rating = qd1
                    q.save()
                if qd2 in [None, '', 'null']:
                    qd2 = '0.5'
                    q = QD2.objects.get(feedback=feedback)
                    q.rating = qd2
                    q.save()

                overall = feedback.get_overall_rating()
                if overall > 2:
                    nb_greens += 1
                else:
                    nb_greys += 1
                overall_rating += overall;
                feedback.timestamp += timedelta(hours=5, minutes=30)
                if feedback.timestamp.date() == today_date:
                    nb_feedbacks_today += 1
                    if overall > 2:
                        nb_greens_today += 1
                    else:
                        nb_greys_today += 1

            if nb_feedbacks > 0:
                overall_rating = float(overall_rating / nb_feedbacks)

            # Storing stat data
            if not StatsBEntity.objects.filter(b_entity=incharge.b_entity).exists():
                StatsBEntity.objects.create(b_entity=incharge.b_entity, overall_rating=overall_rating,
                                            greys=nb_greys, greens=nb_greens, customers=nb_customers)
            if not StatsBEntityDaily.objects.filter(b_entity=incharge.b_entity, date=today_date).exists():
                StatsBEntityDaily.objects.create(b_entity=incharge.b_entity, date=today_date,
                                                 greys=nb_greys_today, greens=nb_greens_today)

        # Updating Stat data
        stats = StatsBEntity.objects.get(b_entity=b_entity)
        stats.overall_rating = ((stats.overall_rating*(stats.greys+stats.greens)) + overall_rating) / \
                               (stats.greys+stats.greens+f_nb_greens+f_nb_greys)
        stats.greens += f_nb_greens
        stats.greys += f_nb_greys
        stats.customers += new_customers
        stats.save()

        today = datetime.now() + timedelta(hours=5, minutes=30)
        today_date = today.date()

        # Updating today data
        if StatsBEntityDaily.objects.filter(b_entity=incharge.b_entity, date=today_date).exists():
            stats_today = StatsBEntityDaily.objects.filter(b_entity=incharge.b_entity, date=today_date)[0]
            stats_today.greys += f_nb_greys
            stats_today.greens += f_nb_greens
            stats_today.save()
        else:
            StatsBEntityDaily.objects.create(b_entity=incharge.b_entity, date=today_date,
                                             greys=f_nb_greys, greens=f_nb_greens)

        hour = today.hour
        try:
            stat = StatsBEntityHourly.objects.get(b_entity=b_entity, date=today_date, hour=hour)
            stat.greys += f_nb_greys
            stat.greens += f_nb_greens
            stat.save()
        except StatsBEntityHourly.DoesNotExist:
            StatsBEntityHourly.objects.create(b_entity=b_entity, date=today_date, hour=hour, greys=f_nb_greys,
                                              greens=f_nb_greens)

        response_data['result'] = 'success'
        response_data['message'] = 'Feedback Sent'
        return HttpResponse(json.dumps(response_data), content_type='application/json')


# Single StatsBEntity
class FeedbackDetail(generics.ListCreateAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    lookup_field = 'b_entity'



