from datetime import datetime, time
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from feedback.models import *
from .forms import *
from feedbackanalysis.util import *
from sms.util import *
from reversion import revisions as reversion
from django.db import transaction
from sms.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from shop.models import AssetAccount, BalanceAccount, BalanceAccountHolder
from django.utils import timezone
from django.db.models import Q


@login_required
def dashboard(request, pk=0):
    if request.user.is_authenticated():
        if pk == 0:
            try:
                incharge = Incharge.objects.get(user=request.user)
                b_entity = incharge.b_entity
            except Incharge.DoesNotExist:
                return redirect('b2b.views.dashboard_register')
        else:
            b_entity = get_object_or_404(BEntity, pk=pk)
            incharge = get_object_or_404(Incharge, b_entity=b_entity)

        today = datetime.now() + timedelta(hours=5, minutes=30)
        today_date = today.date()
        if BalanceAccountHolder.objects.filter(b_entity=b_entity).exists():
            balance = get_object_or_404(BalanceAccountHolder, b_entity=b_entity).balance_account.balance
        else:
            balance_account = BalanceAccount.objects.create()
            balance_account_holder = BalanceAccountHolder.objects.create(b_entity=b_entity,
                                                                         balance_account=balance_account)
            balance = balance_account_holder.balance_account.balance
        data = []
        overall_rating = 0
        nb_feedbacks = 0
        nb_greys = 0
        nb_greens = 0
        nb_feedbacks_today = 0
        nb_greys_today = 0
        nb_greens_today = 0
        if StatsBEntity.objects.filter(b_entity=b_entity).exists():
            stats = get_object_or_404(StatsBEntity, b_entity=b_entity)
            overall_rating = stats.overall_rating
            nb_greys = stats.greys
            nb_greens = stats.greens
            nb_feedbacks = nb_greys + nb_greens
            nb_customers = stats.customers
            if StatsBEntityDaily.objects.filter(b_entity=b_entity, date=today_date).exists():
                stats_daily = get_object_or_404(StatsBEntityDaily, b_entity=b_entity, date=today_date)
                nb_greys_today = stats_daily.greys
                nb_greens_today = stats_daily.greens
                nb_feedbacks_today = nb_greys_today + nb_greens_today
            feedback_list = Feedback.objects.filter(b_entity=b_entity).order_by('-timestamp')[:20]
            for feedback in feedback_list:
                overall = feedback.get_overall_rating()
                feedback.comment = truncatesmart(feedback.comment)
                data.append([feedback, '0', '0', '0', '0', '0', '0', overall])
        else:
            feedback_list = Feedback.objects.filter(b_entity=b_entity).order_by('-timestamp')
            customers = Feedback.objects.filter(b_entity=b_entity).values('customer').distinct()
            nb_customers = len(customers)
            for feedback in feedback_list:
                nb_feedbacks += 1
                qs1 = feedback.get_qs1()
                qs2 = feedback.get_qs2()
                qs3 = feedback.get_qs3()
                qs4 = feedback.get_qs4()
                qd1 = feedback.get_qd1()
                qd2 = feedback.get_qd2()

                if qs1 in [None, '', 'null']:
                    qs1 = '0.5'
                    q = get_object_or_404(QS1, feedback=feedback)
                    q.rating = qs1
                    q.save()
                if qs2 in [None, '', 'null']:
                    qs2 = '0.5'
                    q = get_object_or_404(QS2, feedback=feedback)
                    q.rating = qs2
                    q.save()
                if qs3 in [None, '', 'null']:
                    qs3 = '0.5'
                    q = get_object_or_404(QS3, feedback=feedback)
                    q.rating = qs3
                    q.save()
                if qs4 in [None, '', 'null']:
                    qs4 = '0.5'
                    q = get_object_or_404(QS4, feedback=feedback)
                    q.rating = qs4
                    q.save()
                if qd1 in [None, '', 'null']:
                    qd1 = '0.5'
                    q = get_object_or_404(QD1, feedback=feedback)
                    q.rating = qd1
                    q.save()
                if qd2 in [None, '', 'null']:
                    qd2 = '0.5'
                    q = get_object_or_404(QD2, feedback=feedback)
                    q.rating = qd2
                    q.save()

                overall = feedback.get_overall_rating()
                if overall > 2:
                    nb_greens += 1
                else:
                    nb_greys += 1
                overall_rating += overall
                if feedback.timestamp.date() == today_date:
                    nb_feedbacks_today += 1
                    if overall > 2:
                        nb_greens_today += 1
                    else:
                        nb_greys_today += 1
                feedback.comment = truncatesmart(feedback.comment)
                if nb_feedbacks <= 20:
                    data.append([feedback, qs1, qs2, qs3, qs4, qd1, qd2, overall])

            if nb_feedbacks > 0:
                overall_rating = float(overall_rating/nb_feedbacks)

            # Storing stat data
            if not StatsBEntity.objects.filter(b_entity=b_entity).exists():
                StatsBEntity.objects.create(b_entity=b_entity, overall_rating=overall_rating,
                                            greys=nb_greys, greens=nb_greens, customers=nb_customers)
            if not StatsBEntityDaily.objects.filter(b_entity=b_entity, date=today_date).exists():
                StatsBEntityDaily.objects.create(b_entity=b_entity, date=today_date,
                                                 greys=nb_greys_today, greens=nb_greens_today)
            else:
                stats_today = get_object_or_404(StatsBEntityDaily, b_entity=b_entity, date=today_date)
                stats_today.greys = nb_greys_today
                stats_today.greens = nb_greens_today
                stats_today.save()

        feedbacks = Feedback.objects.filter(b_entity=b_entity).values_list('customer',
                                                                                    flat=True).distinct()
        bdays = []
        annis = []
        now = datetime.now() + timedelta(hours=5, minutes=30)
        month = now.date().month
        day = now.date().day
        for feedback in feedbacks:
            customer = get_object_or_404(Customer, pk=feedback)
            try:
                if ((customer.dt_bday.month == month and customer.dt_bday.day >= day) or
                        (customer.dt_bday.month == month+1)):
                    bdays.append(customer)
            except Exception:
                pass
            try:
                if ((customer.dt_anni.month == month and customer.dt_anni.day >= day) or
                        (customer.dt_anni.month == month + 1)):
                    annis.append(customer)
            except Exception:
                pass

        return render(request, 'b2b/dashboard.html', {
            'pk': pk,
            'incharge': incharge,
            'data': data,
            'balance': balance,
            'bdays': bdays,
            'annis': annis,
            'stats': {
                'total':{
                    'overall_rating': overall_rating,
                    'nb_feedbacks': nb_feedbacks,
                    'nb_greys': nb_greys,
                    'nb_greens': nb_greens,
                    'nb_customers': nb_customers,
                },
                'today': {
                    'nb_feedbacks': nb_feedbacks_today,
                    'nb_greys': nb_greys_today,
                    'nb_greens': nb_greens_today,
                },
            },
        })


@login_required
def dashboard_json(request, pk=0):
    if request.user.is_authenticated():
        if pk == 0:
            try:
                b_entity = Incharge.objects.get(user=request.user).b_entity
            except Incharge.DoesNotExist:
                return redirect('b2b.views.dashboard_register')
        else:
            b_entity = get_object_or_404(BEntity, pk=pk)

        feedbacks = Feedback.objects.filter(b_entity=b_entity).order_by('-timestamp')
        now = datetime.now()
        now += timedelta(hours=5, minutes=30)
        date = now.date()
        week_date_range = get_week_day_range(date)
        month_date_range = get_month_day_range(date)
        year_date_range = get_year_day_range(date)

        total_ratings = [0, 0, 0, 0, 0, 0]

        nb_qd1 = 0
        nb_qd2 = 0
        try:
            qd1_text = QD1Backup.objects.filter(b_entity=b_entity,
                                                q_text=b_entity.qd1_text).order_by('-created_at')[0]
        except IndexError:
            qd1_text = QD1Backup.objects.create(b_entity=b_entity, q_text=b_entity.qd1_text)

        try:
            qd2_text = QD2Backup.objects.filter(b_entity=b_entity,
                                                q_text=b_entity.qd2_text).order_by('-created_at')[0]
        except IndexError:
            qd2_text = QD2Backup.objects.create(b_entity=b_entity, q_text=b_entity.qd2_text)

        feedback_day = [[], []]
        feedback_daily = [[], []]
        rating_day = [[], [], [], [], []]
        rating_daily = [[], [], [], [], []]
        for num in range(0, 24):
            feedback_day[0].append(0)
            feedback_day[1].append(0)
            feedback_daily[0].append(0)
            feedback_daily[1].append(0)
            rating_day[0].append(0)
            rating_day[1].append(0)
            rating_day[2].append(0)
            rating_day[3].append(0)
            rating_day[4].append(0)
            rating_daily[0].append(0)
            rating_daily[1].append(0)
            rating_daily[2].append(0)
            rating_daily[3].append(0)
            rating_daily[4].append(0)

        feedback_week = [[], []]
        feedback_weekly = [[], []]
        rating_week = [[], [], [], [], []]
        rating_weekly = [[], [], [], [], []]
        for num in range(0, 8):
            feedback_week[0].append(0)
            feedback_week[1].append(0)
            feedback_weekly[0].append(0)
            feedback_weekly[1].append(0)
            rating_week[0].append(0)
            rating_week[1].append(0)
            rating_week[2].append(0)
            rating_week[3].append(0)
            rating_week[4].append(0)
            rating_weekly[0].append(0)
            rating_weekly[1].append(0)
            rating_weekly[2].append(0)
            rating_weekly[3].append(0)
            rating_weekly[4].append(0)

        feedback_month = [[], []]
        feedback_monthly = [[], []]
        rating_month = [[], [], [], [], []]
        rating_monthly = [[], [], [], [], []]
        for num in range(0, 32):
            feedback_month[0].append(0)
            feedback_month[1].append(0)
            feedback_monthly[0].append(0)
            feedback_monthly[1].append(0)
            rating_month[0].append(0)
            rating_month[1].append(0)
            rating_month[2].append(0)
            rating_month[3].append(0)
            rating_month[4].append(0)
            rating_monthly[0].append(0)
            rating_monthly[1].append(0)
            rating_monthly[2].append(0)
            rating_monthly[3].append(0)
            rating_monthly[4].append(0)

        feedback_year = [[], []]
        feedback_yearly = [[], []]
        rating_year = [[], [], [], [], []]
        rating_yearly = [[], [], [], [], []]
        for num in range(0, 13):
            feedback_year[0].append(0)
            feedback_year[1].append(0)
            feedback_yearly[0].append(0)
            feedback_yearly[1].append(0)
            rating_year[0].append(0)
            rating_year[1].append(0)
            rating_year[2].append(0)
            rating_year[3].append(0)
            rating_year[4].append(0)
            rating_yearly[0].append(0)
            rating_yearly[1].append(0)
            rating_yearly[2].append(0)
            rating_yearly[3].append(0)
            rating_yearly[4].append(0)

        """
        ////////////
        DATA FILLING
        ///////////
        """
        for feedback in feedbacks:

            """
            ////////////
            PIE CHART
            ///////////
            """
            total_ratings[0] += feedback.get_qs1()
            total_ratings[1] += feedback.get_qs2()
            total_ratings[2] += feedback.get_qs3()
            total_ratings[3] += feedback.get_qs4()

            if feedback.timestamp >= qd1_text.created_at:
                total_ratings[4] += feedback.get_qd1()
                nb_qd1 += 1
            if feedback.timestamp >= qd2_text.created_at:
                total_ratings[5] += feedback.get_qd2()
                nb_qd2 += 1

            feedback_hr = feedback.timestamp.hour
            feedback_date = feedback.timestamp.date()
            """
            ////////////
            FEEDBACK CHART
            ///////////
            """
            f_type = 0
            if feedback.if_green():
                f_type = 1
            feedback_daily[f_type][feedback_hr] += 1
            feedback_weekly[f_type][feedback_date.weekday()] += 1
            feedback_monthly[f_type][feedback_date.day] += 1
            feedback_yearly[f_type][feedback_date.month] += 1
            # Fill today data
            if feedback_date == date:
                feedback_day[f_type][feedback_hr] += 1
            # Fill this week data
            if week_date_range[0] <= feedback_date <= week_date_range[1]:
                feedback_week[f_type][feedback_date.weekday()] += 1
            # Fill this month data
            if month_date_range[0] <= feedback_date <= month_date_range[1]:
                feedback_month[f_type][feedback_date.day] += 1
            # Fill this year data
            if year_date_range[0] <= feedback_date <= year_date_range[1]:
                feedback_year[f_type][feedback_date.month] += 1

            """
            ////////////
            RATING CHART
            ///////////
            """
            ratings = (feedback.get_qs1(), feedback.get_qs2(), feedback.get_qs3(), feedback.get_qs4(),
                   feedback.get_overall_rating())
            i = 0
            for rating in ratings:
                rating_daily[i][feedback_hr] += rating
                rating_weekly[i][feedback_date.weekday()] += rating
                rating_monthly[i][feedback_date.day] += rating
                rating_yearly[i][feedback_date.month] += rating
                # Fill today data
                if feedback_date == date:
                    rating_day[i][feedback_hr] += rating
                # Fill this week data
                if week_date_range[0] <= feedback_date <= week_date_range[1]:
                    rating_week[i][feedback_date.weekday()] += rating
                # Fill this month data
                if month_date_range[0] <= feedback_date <= month_date_range[1]:
                    rating_month[i][feedback_date.day] += rating
                # Fill this year data
                if year_date_range[0] <= feedback_date <= year_date_range[1]:
                    rating_year[i][feedback_date.month] += rating
                i += 1

        # Averaging Rating values
        for f in range(0, 24):
            for j in range(0, 5):
                if not rating_daily[j][f] == 0:
                    rating_daily[j][f] = round(rating_daily[j][f] / (feedback_daily[0][f] + feedback_daily[1][f]), 2)
                if not rating_day[j][f] == 0:
                    rating_day[j][f] = round(rating_day[j][f] / (feedback_day[0][f] + feedback_day[1][f]), 2)
        for f in range(0, 8):
            for j in range(0, 5):
                if not rating_weekly[j][f] == 0:
                    rating_weekly[j][f] = round(rating_weekly[j][f] / (feedback_weekly[0][f] + feedback_weekly[1][f]), 2)
                if not rating_week[j][f] == 0:
                    rating_week[j][f] = round(rating_week[j][f] / (feedback_week[0][f] + feedback_week[1][f]), 2)
        for f in range(0, 32):
            for j in range(0, 5):
                if not rating_monthly[j][f] == 0:
                    rating_monthly[j][f] = round(rating_monthly[j][f] / (feedback_monthly[0][f] + feedback_monthly[1][f]), 2)
                if not rating_month[j][f] == 0:
                    rating_month[j][f] = round(rating_month[j][f] / (feedback_month[0][f] + feedback_month[1][f]), 2)
        for f in range(0, 13):
            for j in range(0, 5):
                if not rating_yearly[j][f] == 0:
                    rating_yearly[j][f] = round(rating_yearly[j][f] / (feedback_yearly[0][f] + feedback_yearly[1][f]), 2)
                if not rating_year[j][f] == 0:
                    rating_year[j][f] = round(rating_year[j][f] / (feedback_year[0][f] + feedback_year[1][f]), 2)

        data = ({
            'feedback': {
                'daily': feedback_daily,
                'weekly': feedback_weekly,
                'monthly': feedback_monthly,
                'yearly': feedback_yearly,
                'day': feedback_day,
                'week': feedback_week,
                'month': feedback_month,
                'year': feedback_year,
            },
            'rating': {
                'daily': rating_daily,
                'weekly': rating_weekly,
                'monthly': rating_monthly,
                'yearly': rating_yearly,
                'day': rating_day,
                'week': rating_week,
                'month': rating_month,
                'year': rating_year,
            },
            'pie': {
                'ratings': total_ratings,
                'nb_feedbacks': len(feedbacks),
                'nb_qd1': nb_qd1,
                'nb_qd2': nb_qd2,
            },
        })
        return JsonResponse(data, safe=False)


@login_required
def dashboard_feedbacks(request):
    if request.user.is_authenticated():
        if Incharge.objects.filter(user=request.user).exists():
            incharge = get_object_or_404(Incharge, user=request.user)
            feedback_list = Feedback.objects.filter(b_entity=incharge.b_entity).order_by('-timestamp')
            data = []
            for feedback in feedback_list:
                qs1 = feedback.get_qs1()
                qs2 = feedback.get_qs2()
                qs3 = feedback.get_qs3()
                qs4 = feedback.get_qs4()
                qd1 = feedback.get_qd1()
                qd2 = feedback.get_qd2()

                if qs1 in [None, '', 'null']:
                    qs1 = '0.5'
                    q = get_object_or_404(QS1, feedback=feedback)
                    q.rating = qs1
                    q.save()
                if qs2 in [None, '', 'null']:
                    qs2 = '0.5'
                    q = get_object_or_404(QS2, feedback=feedback)
                    q.rating = qs2
                    q.save()
                if qs3 in [None, '', 'null']:
                    qs3 = '0.5'
                    q = get_object_or_404(QS3, feedback=feedback)
                    q.rating = qs3
                    q.save()
                if qs4 in [None, '', 'null']:
                    qs4 = '0.5'
                    q = get_object_or_404(QS4, feedback=feedback)
                    q.rating = qs4
                    q.save()
                if qd1 in [None, '', 'null']:
                    qd1 = '0.5'
                    q = get_object_or_404(QD1, feedback=feedback)
                    q.rating = qd1
                    q.save()
                if qd2 in [None, '', 'null']:
                    qd2 = '0.5'
                    q = get_object_or_404(QD2, feedback=feedback)
                    q.rating = qd2
                    q.save()

                try:
                    qs1 = float(qs1)
                except Exception:
                    qs1 = 0.5
                try:
                    qs2 = float(qs2)
                except Exception:
                    qs2 = 0.5
                try:
                    qs3 = float(qs3)
                except Exception:
                    qs3 = 0.5
                try:
                    qs4 = float(qs4)
                except Exception:
                    qs4 = 0.5
                try:
                    qd1 = float(qd1)
                except Exception:
                    qd1 = 0.5
                try:
                    qd2 = float(qd2)
                except Exception:
                    qd2 = 0.5

                overall = feedback.get_overall_rating()
                data.append([feedback, qs1, qs2, qs3, qs4, qd1, qd2, overall])

            paginator = Paginator(data, 25)

            page = request.GET.get('page')
            try:
                feedbacks = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                feedbacks = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                feedbacks = paginator.page(paginator.num_pages)

            return render(request, 'b2b/dashboard_feedbacks.html', {
                'incharge': incharge,
                'data': feedbacks,
            })
        else:
            return redirect('b2b.views.dashboard_register')


@login_required
def dashboard_feedbacks_post(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            form = request.POST
            post = get_object_or_404(Feedback, pk=form.get('id'))
            post.importance = form.get('status')
            post.save()
            return redirect('dashboard_feedbacks')
        return redirect('dashboard_feedbacks')


@transaction.atomic()
@reversion.create_revision()
@login_required
def dashboard_register(request):
    if request.user.is_authenticated():
        user = get_object_or_404(User, pk=request.user.pk)
        if UserProfile.objects.filter(user=request.user.pk).exists():
            return redirect('dashboard')
        else:
            if request.method == "POST":
                form = request.POST
                user.first_name = form.get('first_name')
                user.last_name = form.get('last_name')
                mobile = Mobile.objects.get_or_create(number=form.get('mobile'))[0]
                user.email = form.get('email')
                address = Address.objects.get_or_create(street=form.get('street'), city=form.get('city'),
                                                        state=form.get('state'), country='India',
                                                        zip_code=form.get('zip_code'))[0]
                user.save()
                UserProfile.objects.create(user=user, mobile=mobile, address=address)

                # Creating BEntity
                c_mobile = Mobile.objects.get_or_create(number=form.get('c_mobile'))[0]
                bentity = BEntity.objects.create(name=form.get('c_name'), mobile=c_mobile, email=form.get('c_email'),
                                                 qd1_text='MUSIC', qd2_text='LOCATION')

                # Creating Custom question backup
                QD1Backup.objects.create(b_entity=bentity, q_text='MUSIC')
                QD2Backup.objects.create(b_entity=bentity, q_text='LOCATION')

                # Creating Incharge
                Incharge.objects.create(user=user, b_entity=bentity)

                # Creating Balance Account if it does not exist
                if not BalanceAccountHolder.objects.filter(b_entity=bentity).exists():
                    balance_account = BalanceAccount.objects.create()
                    BalanceAccountHolder.objects.create(b_entity=bentity, balance_account=balance_account)

                balance_account_holder = get_object_or_404(BalanceAccountHolder, b_entity=bentity)

                # Creating Assets Account if it does not exist
                if not AssetAccount.objects.filter(balance_account=balance_account_holder.balance_account).exists():
                    AssetAccount.objects.create(balance_account=balance_account_holder.balance_account)

                # Send Thank You for Registration SMS
                mobile_list = list()
                message = urlquote("Dear Business Partner, Thank you for registering with us")
                mobile_list.append(str(mobile))
                send_message(mobile_list, message)

                return redirect('dashboard')
        return render(request, 'b2b/dashboard_register.html', {})


@login_required
def dashboard_profile(request):
    incharge = get_object_or_404(Incharge, user=request.user)
    if UserProfile.objects.filter(user=request.user).exists():
        profile = get_object_or_404(UserProfile, user=request.user)
        if request.user.is_authenticated():
            return render(request, 'b2b/dashboard_profile.html', {
                'user': incharge,
                'profile': profile,
            })
    else:
        return redirect('dashboard_profile_edit')


@transaction.atomic()
@reversion.create_revision()
@login_required
def dashboard_profile_edit(request):
    if request.user.is_authenticated():
        user = get_object_or_404(User, pk=request.user.pk)
        if UserProfile.objects.filter(user=request.user.pk).exists():
            profile = get_object_or_404(UserProfile, user=request.user.pk)
            if request.method == "POST":
                form = request.POST
                user.first_name = form.get('first_name')
                user.last_name = form.get('last_name')
                profile.mobile = Mobile.objects.get_or_create(number=form.get('mobile'))[0]
                user.email = form.get('email')
                profile.address = Address.objects.get_or_create(street=form.get('street'), city=form.get('city'),
                                                             state=form.get('state'), country='India',
                                                             zip_code=form.get('zip_code'))[0]
                user.save()
                profile.save()
                return redirect('dashboard_profile')
            return render(request, 'b2b/dashboard_profile_edit.html', {
                'user': user,
                'profile': profile,
            })
        else:
            if request.method == "POST":
                form = request.POST
                user.first_name = form.get('first_name')
                user.last_name = form.get('last_name')
                mobile = Mobile.objects.get_or_create(number=form.get('mobile'))[0]
                user.email = form.get('email')
                address = Address.objects.get_or_create(street=form.get('street'), city=form.get('city'),
                                                                state=form.get('state'), country='India',
                                                                zip_code=form.get('zip_code'))[0]
                user.save()
                UserProfile.objects.create(user=user, mobile=mobile, address=address)

                # Send Thank You for Registration SMS
                mobile_list = list()
                message = urlquote("Dear Business Partner, Thank you for registering with us")
                mobile_list.append(str(mobile))
                send_message(mobile_list, message)

                return redirect('dashboard_profile')
        return render(request, 'b2b/dashboard_profile_edit.html', {
            'user': user,
        })


@transaction.atomic()
@reversion.create_revision()
@login_required
def dashboard_custom_questions_edit(request):
    incharge = get_object_or_404(Incharge, user=request.user)
    post = get_object_or_404(BEntity, pk=incharge.b_entity.pk)
    if request.user.is_authenticated():
        if request.method == "POST":
            form = request.POST
            # Creating backup
            if post.qd1_text != form.get('qd1'):
                QD1Backup.objects.create(b_entity=post, q_text=form.get('qd1'))
            if post.qd2_text != form.get('qd2'):
                QD2Backup.objects.create(b_entity=post, q_text=form.get('qd2'))
            post.qd1_text = form.get('qd1')
            post.qd2_text = form.get('qd2')
            post.save()
            return redirect('dashboard')
        return redirect('dashboard')

@transaction.atomic()
@reversion.create_revision()
@login_required
def dashboard_bentity(request):
    incharge = get_object_or_404(Incharge, user=request.user)
    b_entity = get_object_or_404(BEntity, pk=incharge.b_entity.pk)
    if request.method == "POST":
        form = request.POST
        if form.get("submit") == "add_alert_list":
            name = form.get('name')
            email = form.get('email')
            mobile = Mobile.objects.get_or_create(number=form.get('mobile'))[0]

            nfa_sms = False
            nfa_email = False
            daily_report_sms = False
            daily_report_email = False

            if form.get('nfa_sms'):
                nfa_sms = True
            if form.get('nfa_email'):
                nfa_email = True
            if form.get('daily_report_sms'):
                daily_report_sms = True
            if form.get('daily_report_email'):
                daily_report_email = True

            AlertList.objects.create(b_entity=b_entity, name=name, mobile=mobile, email=email, nfa_sms=nfa_sms,
                                     nfa_email=nfa_email, daily_report_sms=daily_report_sms,
                                     daily_report_email=daily_report_email)
        elif form.get("submit") == "delete_alert_list":
            pk = form.get('nfa_pk')
            alert = get_object_or_404(AlertList, pk=pk)
            alert.archive = True
            alert.save()
        elif form.get("submit") == "nfa_sms":
            pk = int(form.get('id'))
            alert = get_object_or_404(AlertList, pk=pk)
            if form.get('status') == 'true':
                alert.nfa_sms = True
            else:
                alert.nfa_sms = False
            alert.save()
        elif form.get("submit") == "nfa_email":
            pk = int(form.get('id'))
            alert = get_object_or_404(AlertList, pk=pk)
            if form.get('status') == 'true':
                alert.nfa_email = True
            else:
                alert.nfa_email = False
            alert.save()
        elif form.get("submit") == "daily_report_sms":
            pk = int(form.get('id'))
            alert = get_object_or_404(AlertList, pk=pk)
            if form.get('status') == 'true':
                alert.daily_report_sms = True
            else:
                alert.daily_report_sms = False
            alert.save()
        elif form.get("submit") == "daily_report_email":
            pk = int(form.get('id'))
            alert = get_object_or_404(AlertList, pk=pk)
            if form.get('status') == 'true':
                alert.daily_report_email = True
            else:
                alert.daily_report_email = False
            alert.save()

    if not BalanceAccountHolder.objects.filter(b_entity=b_entity).exists():
        balance_account = BalanceAccount.objects.create()
        BalanceAccountHolder.objects.create(b_entity=b_entity, balance_account=balance_account)

    balance_account_holder = get_object_or_404(BalanceAccountHolder, b_entity=b_entity)

    if not AssetAccount.objects.filter(balance_account=balance_account_holder.balance_account).exists():
        AssetAccount.objects.create(balance_account=balance_account_holder.balance_account)
    asset_account = get_object_or_404(AssetAccount, balance_account=balance_account_holder.balance_account)
    alert_list = AlertList.objects.filter(b_entity=b_entity, archive=False)
    return render(request, 'b2b/dashboard_bentity.html', {
        'b_entity': b_entity,
        'balance_account': balance_account_holder.balance_account,
        'asset_account': asset_account,
        'alert_list': alert_list,
    })


@transaction.atomic()
@reversion.create_revision()
@login_required
def dashboard_bentity_edit(request):
    if request.user.is_authenticated():
        incharge = get_object_or_404(Incharge, user=request.user)
        post = get_object_or_404(BEntity, pk=incharge.b_entity.pk)
        if request.method == "POST":
            form = request.POST
            post.name = form.get('name')
            post.mobile = Mobile.objects.get_or_create(number=form.get('mobile'))[0]
            post.email = form.get('email')
            post.fax = form.get('fax')
            post.address = Address.objects.get_or_create(street=form.get('street'), city=form.get('city'),
                                                         state=form.get('state'), country='India',
                                                         zip_code=form.get('zip_code'))[0]
            post.save()
            return redirect('dashboard_bentity')
        return render(request, 'b2b/dashboard_bentity_edit.html', {
            'form': post
        })


@transaction.atomic()
@reversion.create_revision()
@login_required
def dashboard_employees(request):
    if request.user.is_authenticated():
        now = datetime.now() + timedelta(hours=5, minutes=30)
        date = now.date()
        date_range = get_month_day_range(date)
        incharge = get_object_or_404(Incharge, user=request.user)
        employees = Employee.objects.filter(b_entity=incharge.b_entity.pk, active=True)
        total_feedbacks = Feedback.objects.filter(b_entity=incharge.b_entity.pk)
        employee_list = []
        for employee in employees:
            total_overall = 0
            max_overall = 0
            feedbacks = Feedback.objects.filter(employee=employee, timestamp__range=(date_range[0], date_range[1]))
            p_feedbacks = 0
            if len(total_feedbacks) > 0:
                p_feedbacks = (float(len(feedbacks)) / len(total_feedbacks)) * 100
            for feedback in feedbacks:
                total_overall += feedback.get_overall_rating()
                max_overall += 5
            if(max_overall > 0):
                score = (total_overall / max_overall) * 100
            else:
                score = 0
            employee_list.append({'employee': employee, 'score':score,
                                  'nb_feedbacks': len(feedbacks), 'p_feedbacks': p_feedbacks})
        if request.method == "POST":
            incharge = get_object_or_404(Incharge, user=request.user)
            b_entity = get_object_or_404(BEntity, pk=incharge.b_entity.pk)
            form = request.POST
            mobile = Mobile.objects.get_or_create(number=form.get('mobile'))[0]
            if form.get('pk'):
                post = get_object_or_404(Employee, pk=int(form.get('pk')))
                post.first_name = form.get('first_name')
                post.last_name = form.get('last_name')
                post.mobile = mobile
                pin = form.get('pin')
                if pin in [None, '', 'null']:
                    pin = generate_pin()
                post.pin = pin
                post.save()
            else:
                pin = form.get('pin')
                if pin in [None, '', 'null']:
                    pin = generate_pin()
                employee, created = Employee.objects.get_or_create(first_name=form.get('first_name'), b_entity=b_entity,
                                                                   pin=pin, last_name=form.get('last_name'),
                                                                   mobile=mobile)
                employee.active = True
                employee.save()
                # Employee PIN confirmation SMS
                mobile_list = list()
                message = str(pin)+"%20is%20your%20FA%20feedback%20login%20pin"
                mobile_list.append(str(mobile))
                send_message(mobile_list, message)
            return redirect('dashboard_employees')
        return render(request, 'b2b/dashboard_employees.html', {
            'employees': employee_list,
        })


@transaction.atomic()
@reversion.create_revision()
@login_required
def dashboard_employee_edit(request, pk):
    incharge = get_object_or_404(Incharge, user=request.user)
    employees = Employee.objects.filter(b_entity=incharge.b_entity.pk, active=True)
    employee_list = []
    for employee in employees:
        total_overall = 0
        max_overall = 0
        feedbacks = Feedback.objects.filter(employee=employee)
        for feedback in feedbacks:
            total_overall += feedback.get_overall_rating()
            max_overall += 5
        if (max_overall > 0):
            score = (total_overall / max_overall) * 100
        else:
            score = 0
        employee_list.append({'employee': employee, 'score': score, 'nb_feedbacks': len(feedbacks)})
    post = get_object_or_404(Employee, pk=pk)
    return render(request, 'b2b/dashboard_employees.html', {
        'form': post,
        'employees': employee_list
    })


@transaction.atomic()
@reversion.create_revision()
@login_required
def dashboard_employee_remove(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.active = False
    employee.save()
    return redirect('b2b.views.dashboard_employees')


@transaction.atomic()
@reversion.create_revision()
@login_required
def dashboard_employee(request, pk):
    if request.user.is_authenticated():
        incharge = get_object_or_404(Incharge, user=request.user)
        employee = get_object_or_404(Employee, pk=pk, b_entity=incharge.b_entity.pk)
        feedback_list = Feedback.objects.filter(b_entity=incharge.b_entity.pk, employee=employee.pk).\
            order_by('-timestamp')
        data = []
        for feedback in feedback_list:
            qs1 = feedback.get_qs1()
            qs2 = feedback.get_qs2()
            qs3 = feedback.get_qs3()
            qs4 = feedback.get_qs4()
            qd1 = feedback.get_qd1()
            qd2 = feedback.get_qd2()

            if qs1 in [None, '', 'null']:
                qs1 = '0.5'
                q = get_object_or_404(QS1, feedback=feedback)
                q.rating = qs1
                q.save()
            if qs2 in [None, '', 'null']:
                qs2 = '0.5'
                q = get_object_or_404(QS2, feedback=feedback)
                q.rating = qs2
                q.save()
            if qs3 in [None, '', 'null']:
                qs3 = '0.5'
                q = get_object_or_404(QS3, feedback=feedback)
                q.rating = qs3
                q.save()
            if qs4 in [None, '', 'null']:
                qs4 = '0.5'
                q = get_object_or_404(QS4, feedback=feedback)
                q.rating = qs4
                q.save()
            if qd1 in [None, '', 'null']:
                qd1 = '0.5'
                q = get_object_or_404(QD1, feedback=feedback)
                q.rating = qd1
                q.save()
            if qd2 in [None, '', 'null']:
                qd2 = '0.5'
                q = get_object_or_404(QD2, feedback=feedback)
                q.rating = qd2
                q.save()

            overall = feedback.get_overall_rating()
            data.append([feedback, qs1, qs2, qs3, qs4, qd1, qd2, overall])

        paginator = Paginator(data, 25)

        page = request.GET.get('page')
        try:
            feedbacks = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            feedbacks = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            feedbacks = paginator.page(paginator.num_pages)

        return render(request, 'b2b/dashboard_employee.html', {
            'data': feedbacks,
            'employee': employee
        })


@login_required
def dashboard_employee_json(request, pk):
    if request.user.is_authenticated():
        incharge = get_object_or_404(Incharge, user=request.user)
        feedbacks = Feedback.objects.filter(b_entity=incharge.b_entity, employee=pk).order_by('-timestamp')
        now = datetime.now()
        now += timedelta(hours=5, minutes=30)
        date = now.date()
        week_date_range = get_week_day_range(date)
        month_date_range = get_month_day_range(date)
        year_date_range = get_year_day_range(date)

        feedback_day = [[], []]
        feedback_daily = [[], []]
        for num in range(0, 24):
            feedback_day[0].append(0)
            feedback_day[1].append(0)
            feedback_daily[0].append(0)
            feedback_daily[1].append(0)

        feedback_week = [[], []]
        feedback_weekly = [[], []]
        rating_week = [[], [], [], [], []]
        rating_weekly = [[], [], [], [], []]
        for num in range(0, 8):
            feedback_week[0].append(0)
            feedback_week[1].append(0)
            feedback_weekly[0].append(0)
            feedback_weekly[1].append(0)

        feedback_month = [[], []]
        feedback_monthly = [[], []]
        rating_month = [[], [], [], [], []]
        rating_monthly = [[], [], [], [], []]
        for num in range(0, 32):
            feedback_month[0].append(0)
            feedback_month[1].append(0)
            feedback_monthly[0].append(0)
            feedback_monthly[1].append(0)

        feedback_year = [[], []]
        feedback_yearly = [[], []]
        rating_year = [[], [], [], [], []]
        rating_yearly = [[], [], [], [], []]
        for num in range(0, 13):
            feedback_year[0].append(0)
            feedback_year[1].append(0)
            feedback_yearly[0].append(0)
            feedback_yearly[1].append(0)

        """
        ////////////
        DATA FILLING
        ///////////
        """
        for feedback in feedbacks:
            feedback_hr = feedback.timestamp.hour
            feedback_date = feedback.timestamp.date()
            """
            ////////////
            FEEDBACK CHART
            ///////////
            """
            f_type = 0
            if feedback.get_qs4() > 2:
                f_type = 1
            feedback_daily[f_type][feedback_hr] += 1
            feedback_weekly[f_type][feedback_date.weekday()] += 1
            feedback_monthly[f_type][feedback_date.day] += 1
            feedback_yearly[f_type][feedback_date.month] += 1
            # Fill today data
            if feedback_date == date:
                feedback_day[f_type][feedback_hr] += 1
            # Fill this week data
            if week_date_range[0] <= feedback_date <= week_date_range[1]:
                feedback_week[f_type][feedback_date.weekday()] += 1
            # Fill this month data
            if month_date_range[0] <= feedback_date <= month_date_range[1]:
                feedback_month[f_type][feedback_date.day] += 1
            # Fill this year data
            if year_date_range[0] <= feedback_date <= year_date_range[1]:
                feedback_year[f_type][feedback_date.month] += 1

        data = ({
            'feedback': {
                'daily': feedback_daily,
                'weekly': feedback_weekly,
                'monthly': feedback_monthly,
                'yearly': feedback_yearly,
                'day': feedback_day,
                'week': feedback_week,
                'month': feedback_month,
                'year': feedback_year,
            },
        })
        return JsonResponse(data, safe=False)


@login_required
def dashboard_feedbacks_glimpse(request):
    if request.user.is_authenticated():
        if Incharge.objects.filter(user=request.user).exists():
            incharge = get_object_or_404(Incharge, user=request.user)
            feedback_list = Feedback.objects.filter(b_entity=incharge.b_entity).order_by('-timestamp')
            data = []
            for feedback in feedback_list:
                qs1 = feedback.get_qs1()
                qs2 = feedback.get_qs2()
                qs3 = feedback.get_qs3()
                qs4 = feedback.get_qs4()
                qd1 = feedback.get_qd1()
                qd2 = feedback.get_qd2()

                if qs1 in [None, '', 'null']:
                    qs1 = '0.5'
                    q = get_object_or_404(QS1, feedback=feedback)
                    q.rating = qs1
                    q.save()
                if qs2 in [None, '', 'null']:
                    qs2 = '0.5'
                    q = get_object_or_404(QS2, feedback=feedback)
                    q.rating = qs2
                    q.save()
                if qs3 in [None, '', 'null']:
                    qs3 = '0.5'
                    q = get_object_or_404(QS3, feedback=feedback)
                    q.rating = qs3
                    q.save()
                if qs4 in [None, '', 'null']:
                    qs4 = '0.5'
                    q = get_object_or_404(QS4, feedback=feedback)
                    q.rating = qs4
                    q.save()
                if qd1 in [None, '', 'null']:
                    qd1 = '0.5'
                    q = get_object_or_404(QD1, feedback=feedback)
                    q.rating = qd1
                    q.save()
                if qd2 in [None, '', 'null']:
                    qd2 = '0.5'
                    q = get_object_or_404(QD2, feedback=feedback)
                    q.rating = qd2
                    q.save()

                overall = feedback.get_overall_rating()
                data.append([feedback, qs1, qs2, qs3, qs4, qd1, qd2, overall])

            paginator = Paginator(data, 25)

            page = request.GET.get('page')
            try:
                feedbacks = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                feedbacks = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                feedbacks = paginator.page(paginator.num_pages)

            return render(request, 'b2b/dashboard_feedbacks_glimpse.html', {
                'incharge': incharge,
                'data': feedbacks,
            })
        else:
            return redirect('b2b.views.dashboard_register')


@login_required
def dashboard_customers(request):
    if request.user.is_authenticated():
        incharge = get_object_or_404(Incharge, user=request.user)
        feedbacks = Feedback.objects.filter(b_entity=incharge.b_entity).values_list('customer', flat=True).distinct()
        customers = []
        for feedback in feedbacks:
            customer = get_object_or_404(Customer, pk=feedback)
            feebacks_by_customer = Feedback.objects.filter(customer=customer, b_entity=incharge.b_entity)\
                .order_by('-timestamp')
            customers.append({'customer': customer,
                              'feedback': feebacks_by_customer[0], 'nb_feedbacks': len(feebacks_by_customer)})

        paginator = Paginator(customers, 25)

        page = request.GET.get('page')
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            data = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            data = paginator.page(paginator.num_pages)

        return render(request, 'b2b/dashboard_customers.html', {
            'incharge': incharge,
            'customers': data,
        })


@login_required
def dashboard_customer(request, pk):
    if request.user.is_authenticated():
        incharge = get_object_or_404(Incharge, user=request.user)
        customer = get_object_or_404(Customer, pk=pk)
        feedback_list = Feedback.objects.filter(b_entity=incharge.b_entity.pk, customer=customer.pk)
        data = []
        for feedback in feedback_list:
            qs1 = feedback.get_qs1()
            qs2 = feedback.get_qs2()
            qs3 = feedback.get_qs3()
            qs4 = feedback.get_qs4()
            qd1 = feedback.get_qd1()
            qd2 = feedback.get_qd2()

            if qs1 in [None, '', 'null']:
                qs1 = '0.5'
                q = get_object_or_404(QS1, feedback=feedback)
                q.rating = qs1
                q.save()
            if qs2 in [None, '', 'null']:
                qs2 = '0.5'
                q = get_object_or_404(QS2, feedback=feedback)
                q.rating = qs2
                q.save()
            if qs3 in [None, '', 'null']:
                qs3 = '0.5'
                q = get_object_or_404(QS3, feedback=feedback)
                q.rating = qs3
                q.save()
            if qs4 in [None, '', 'null']:
                qs4 = '0.5'
                q = get_object_or_404(QS4, feedback=feedback)
                q.rating = qs4
                q.save()
            if qd1 in [None, '', 'null']:
                qd1 = '0.5'
                q = get_object_or_404(QD1, feedback=feedback)
                q.rating = qd1
                q.save()
            if qd2 in [None, '', 'null']:
                qd2 = '0.5'
                q = get_object_or_404(QD2, feedback=feedback)
                q.rating = qd2
                q.save()

            overall = feedback.get_overall_rating()
            data.append([feedback, qs1, qs2, qs3, qs4, qd1, qd2, overall])
        return render(request, 'b2b/dashboard_customer.html', {
            'data': data,
        })


@login_required
def dashboard_nfa(request):
    if request.user.is_authenticated():
        if Incharge.objects.filter(user=request.user).exists():
            incharge = get_object_or_404(Incharge, user=request.user)
            feedback_list = Feedback.objects.filter(b_entity=incharge.b_entity).order_by('-timestamp')
            data = []
            for feedback in feedback_list:
                qs1 = feedback.get_qs1()
                qs2 = feedback.get_qs2()
                qs3 = feedback.get_qs3()
                qs4 = feedback.get_qs4()
                qd1 = feedback.get_qd1()
                qd2 = feedback.get_qd2()

                if qs1 in [None, '', 'null']:
                    qs1 = '0.5'
                    q = get_object_or_404(QS1, feedback=feedback)
                    q.rating = qs1
                    q.save()
                if qs2 in [None, '', 'null']:
                    qs2 = '0.5'
                    q = get_object_or_404(QS2, feedback=feedback)
                    q.rating = qs2
                    q.save()
                if qs3 in [None, '', 'null']:
                    qs3 = '0.5'
                    q = get_object_or_404(QS3, feedback=feedback)
                    q.rating = qs3
                    q.save()
                if qs4 in [None, '', 'null']:
                    qs4 = '0.5'
                    q = get_object_or_404(QS4, feedback=feedback)
                    q.rating = qs4
                    q.save()
                if qd1 in [None, '', 'null']:
                    qd1 = '0.5'
                    q = get_object_or_404(QD1, feedback=feedback)
                    q.rating = qd1
                    q.save()
                if qd2 in [None, '', 'null']:
                    qd2 = '0.5'
                    q = get_object_or_404(QD2, feedback=feedback)
                    q.rating = qd2
                    q.save()

                try:
                    qs1 = float(qs1)
                except Exception:
                    qs1 = 0.5
                try:
                    qs2 = float(qs2)
                except Exception:
                    qs2 = 0.5
                try:
                    qs3 = float(qs3)
                except Exception:
                    qs3 = 0.5
                try:
                    qs4 = float(qs4)
                except Exception:
                    qs4 = 0.5
                try:
                    qd1 = float(qd1)
                except Exception:
                    qd1 = 0.5
                try:
                    qd2 = float(qd2)
                except Exception:
                    qd2 = 0.5

                if feedback.get_overall_rating() <= 2 or qs3 <= 2 or qs4 <= 2:
                    overall = feedback.get_overall_rating()
                    data.append([feedback, qs1, qs2, qs3, qs4, qd1, qd2, overall])

            paginator = Paginator(data, 25)

            page = request.GET.get('page')
            try:
                feedbacks = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                feedbacks = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                feedbacks = paginator.page(paginator.num_pages)

            return render(request, 'b2b/dashboard_feedbacks.html', {
                'incharge': incharge,
                'data': feedbacks,
            })
        else:
            return redirect('b2b.views.dashboard_register')


@login_required
def dashboard_promosms(request):
    success=''
    incharge = get_object_or_404(Incharge, user=request.user)
    bentity = get_object_or_404(BEntity, pk=incharge.b_entity.pk)
    balance_account_holder = get_object_or_404(BalanceAccountHolder, b_entity=bentity)
    asset_account = get_object_or_404(AssetAccount, balance_account=balance_account_holder.balance_account)
    promosms_list = PromoSMS.objects.filter(Q(b_entity=bentity, archive=False) | Q(type="COMMON", active=True,
                                                                                   archive=False))
    if not SMSAccount.objects.filter(asset_account=asset_account, active=True, archive=False).exists():
        return render(request, 'b2b/dashboard_promosms.html', {
            'promosms_list': promosms_list,
            'asset_account': asset_account,
            'account_error': 'Contact the administrator to activate your SMS Account!'
        })
    elif asset_account.sms_promo <= 0:
        return render(request, 'b2b/dashboard_promosms.html', {
            'promosms_list': promosms_list,
            'asset_account': asset_account,
            'account_error': 'Your SMS Balance is zero. Please recharge.'
        })
    elif asset_account.sms_promo_validity <= timezone.now() + timedelta(hours=5, minutes=30):
        return render(request, 'b2b/dashboard_promosms.html', {
            'promosms_list': promosms_list,
            'asset_account': asset_account,
            'expired': 'Promo SMS Validity has Expired! '
        })
    else:
        if request.method == "POST":
            form = request.POST
            if form.get("submit") == "delete_promo":
                pk = form.get('promosms_pk')
                promosms = get_object_or_404(PromoSMS, pk=pk)
                promosms.archive = True
                promosms.save()
                success = 'Success! Promo SMS template has been deleted !'
            else:
                PromoSMS.objects.create(b_entity=bentity, title=form.get('title'), content=form.get('content'),
                                        active=False, archive=False)
                success = 'Success! Promo SMS template will be activated within 24hrs.'
        return render(request, 'b2b/dashboard_promosms.html', {
            'promosms_list': promosms_list,
            'asset_account': asset_account,
            'success': success,
        })


@login_required
def dashboard_promosms_customers(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            form = request.POST
            if form.get("submit") == "send_sms":
                customers_pk = form.getlist("customer")
                template_id = form.get('template_id')
                template = get_object_or_404(PromoSMS, pk=template_id)
                incharge = get_object_or_404(Incharge, user=request.user)
                bentity = get_object_or_404(BEntity, pk=incharge.b_entity.pk)
                if template.b_entity == bentity:
                    balance_account_holder = get_object_or_404(BalanceAccountHolder, b_entity=bentity)
                    asset_account = get_object_or_404(AssetAccount, balance_account=balance_account_holder.balance_account)
                    now = timezone.now()
                    if asset_account.sms_promo_validity >= now:
                        sms_account = get_object_or_404(SMSAccount, asset_account=asset_account, active=True,
                                                        archive=False)
                        # Send Promo SMS
                        mobile_list = list()
                        message = urlquote(template.content)
                        for customer_pk in customers_pk:
                            mobile = get_object_or_404(Customer, pk=customer_pk).mobile
                            mobile_list.append(str(mobile))
                        if asset_account.sms_promo > len(mobile_list):
                            send_promo_message(sms_account.loginid, sms_account.password, mobile_list, message)
                            asset_account.sms_promo -= len(mobile_list)
                            asset_account.save()
                            PromoSMSStats.objects.create(user=request.user, promo_sms=template, nb_sms=len(mobile_list))
            if form.get("submit") == "send_sms_filter":
                customer_list = []
                template_id = form.get('template_id')
                template = get_object_or_404(PromoSMS, pk=template_id)
                incharge = get_object_or_404(Incharge, user=request.user)
                bentity = get_object_or_404(BEntity, pk=incharge.b_entity.pk)
                if template.b_entity == bentity:
                    balance_account_holder = get_object_or_404(BalanceAccountHolder, b_entity=bentity)
                    asset_account = get_object_or_404(AssetAccount,
                                                      balance_account=balance_account_holder.balance_account)
                    now = timezone.now()
                    if asset_account.sms_promo_validity >= now:
                        sms_account = get_object_or_404(SMSAccount, asset_account=asset_account, active=True,
                                                        archive=False)
                        feedbacks_by_customer = Feedback.objects.filter(b_entity=incharge.b_entity).\
                            values_list('customer', flat=True).distinct()

                        for feedback_pk in feedbacks_by_customer:
                            feedback = get_object_or_404(Feedback, pk=feedback_pk)
                            happy = False
                            comment = False
                            returning = False
                            if feedback.if_green:
                                happy = True
                            if feedback.comment != '' or feedback.comment:
                                comment = True
                            time_passed = timezone.now() - feedback.timestamp
                            if int(time_passed.days) <= 30:
                                returning = True
                            customer_list.append({
                                'customer': feedback.customer,
                                'happy': happy,
                                'comment': comment,
                                'returning': returning,
                            })

                        print customer_list

                        # Send Promo SMS
                        mobile_list = list()
                        message = urlquote(template.content)
                        if form.get('all'):
                            for customer in customer_list:
                                mobile = get_object_or_404(Customer, pk=customer['customer'].pk).mobile
                                mobile_list.append(str(mobile))
                        else:
                            if form.get('happy'):
                                for customer in customer_list:
                                    if customer['happy']:
                                        mobile = customer['customer'].mobile
                                        mobile_list.append(str(mobile))
                            if form.get('unhappy'):
                                for customer in customer_list:
                                    if not customer['happy']:
                                        mobile = customer['customer'].mobile
                                        mobile_list.append(str(mobile))
                            if form.get('comment'):
                                for customer in customer_list:
                                    if customer['comment']:
                                        mobile = customer['customer'].mobile
                                        mobile_list.append(str(mobile))
                            if form.get('no_comment'):
                                for customer in customer_list:
                                    if not customer['comment']:
                                        mobile = customer['customer'].mobile
                                        mobile_list.append(str(mobile))
                            if form.get('returning'):
                                for customer in customer_list:
                                    if customer['returning']:
                                        mobile = customer['customer'].mobile
                                        mobile_list.append(str(mobile))
                            if form.get('no_returning'):
                                for customer in customer_list:
                                    if not customer['returning']:
                                        mobile = customer['customer'].mobile
                                        mobile_list.append(str(mobile))
                        mobile_list = set(mobile_list) # Remove repetetive numbers
                        if asset_account.sms_promo > len(mobile_list):
                            send_promo_message(sms_account.loginid, sms_account.password, mobile_list, message)
                            asset_account.sms_promo -= len(mobile_list)
                            asset_account.save()
                            PromoSMSStats.objects.create(user=request.user, promo_sms=template, nb_sms=len(mobile_list))
            else:
                template_id = form.get('template_id')
                incharge = get_object_or_404(Incharge, user=request.user)
                feedbacks = Feedback.objects.filter(b_entity=incharge.b_entity).values('customer').distinct()
                customers = []
                for feedback in feedbacks:
                    customer = get_object_or_404(Customer, pk=feedback['customer'])
                    feebacks_by_customer = Feedback.objects.filter(customer=customer, b_entity=incharge.b_entity) \
                        .order_by('-timestamp')
                    time_passed = timezone.now() - feebacks_by_customer[0].timestamp
                    returning = True
                    if int(time_passed.days) > 30:
                        returning = False
                    customers.append({'customer': customer, 'returning': returning,
                                      'feedback': feebacks_by_customer[0], 'nb_feedbacks': len(feebacks_by_customer)})
                return render(request, 'b2b/dashboard_promosms_customers.html', {
                    'incharge': incharge,
                    'customers': customers,
                    'template_id': template_id,
                })
    return redirect('b2b.views.dashboard_promosms')


@login_required
def dashboard_promosms_history(request):
    promos = PromoSMSStats.objects.filter(user=request.user).order_by('-created_at')
    for promo in promos:
        promo.created_at += timedelta(hours=5, minutes=30)
    return render(request, 'b2b/dashboard_promosms_history.html', {
        'promos': promos,
    })

@login_required
def dashboard_owner(request):
    if BEntityAccess.objects.filter(user=request.user).exists():
        bentities_list = []
        feedbacks_list = []
        access_list = BEntityAccess.objects.filter(user=request.user)
        for access in access_list:
            bentities_list.append(access.b_entity)

        overall_rating = 0
        nb_feedbacks = 0
        nb_greys = 0
        nb_greens = 0
        nb_customers = 0
        nb_feedbacks_today = 0
        nb_greys_today = 0
        nb_greens_today = 0

        for bentity in bentities_list:
            feedbacks = Feedback.objects.filter(b_entity=bentity).order_by('-timestamp')[:10]
            for feedback in feedbacks:
                feedbacks_list.append(feedback)
            try:
                stats = StatsBEntity.objects.get(b_entity=bentity)
            except StatsBEntity.DoesNotExist:
                stats = StatsBEntity.objects.create(b_entity=bentity)
            nb_feedbacks += (stats.greens + stats.greys)
            nb_greens += stats.greens
            nb_greys += stats.greys
            nb_customers += stats.customers
            overall_rating += stats.overall_rating

            try:
                stats_daily = StatsBEntityDaily.objects.get(b_entity=bentity, date=datetime.now().date())
            except StatsBEntityDaily.DoesNotExist:
                stats_daily = StatsBEntityDaily.objects.create(b_entity=bentity)
            nb_feedbacks_today += (stats_daily.greens + stats_daily.greys)
            nb_greens_today += stats_daily.greens
            nb_greys_today += stats_daily.greys

        overall_rating = overall_rating / len(bentities_list)

        return render(request, 'b2b/dashboard_owner.html', {
            'user': request.user,
            'bentities': bentities_list,
            'feedbacks': feedbacks_list,
            'stats': {
                'total': {
                    'overall_rating': overall_rating,
                    'nb_feedbacks': nb_feedbacks,
                    'nb_greys': nb_greys,
                    'nb_greens': nb_greens,
                    'nb_customers': nb_customers,
                },
                'today': {
                    'nb_feedbacks': nb_feedbacks_today,
                    'nb_greys': nb_greys_today,
                    'nb_greens': nb_greens_today,
                },
            },
        })
    else:
        return redirect('b2b.views.dashboard')


@login_required
def dashboard_owner_json(request):
    if BEntityAccess.objects.filter(user=request.user).exists():
        bentities_list = []
        access_list = BEntityAccess.objects.filter(user=request.user)
        for access in access_list:
            bentities_list.append(access.b_entity)
        names = []
        greys = {'all': [], 'today': []}
        greens = {'all': [], 'today': []}
        customers = []
        overall_ratings = []
        for bentity in bentities_list:
            names.append(bentity.name)
            try:
                stats = StatsBEntity.objects.get(b_entity=bentity)
            except StatsBEntity.DoesNotExist:
                stats = StatsBEntity.objects.create(b_entity=bentity)

            try:
                stats_daily = StatsBEntityDaily.objects.get(b_entity=bentity, date=datetime.now().date())
            except StatsBEntityDaily.DoesNotExist:
                stats_daily = StatsBEntityDaily.objects.create(b_entity=bentity)

            greys['all'].append(stats.greys)
            greys['today'].append(stats_daily.greys)
            greens['all'].append(stats.greens)
            greens['today'].append(stats_daily.greens)
            customers.append(stats.customers)
            overall_ratings.append(stats.overall_rating)

        data = ({
            'names': names,
            'greys': greys,
            'greens': greens,
            'customers': customers,
            'overall_ratings': overall_ratings,
        })
        return JsonResponse(data, safe=False)
