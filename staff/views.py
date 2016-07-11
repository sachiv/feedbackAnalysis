from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from feedback.models import *
from sms.models import *
from shop.util import *
from django.utils.encoding import smart_unicode
import csv
from django.utils.dateparse import parse_datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active and user.is_staff:
                login(request, user)
                return redirect('staff_dashboard')
            else:
                return render(request, 'staff/login.html', {
                    'notify': 'Access Denied!'
                })
        else:
            return render(request, 'staff/login.html', {
                'notify': 'Invalid Credentials!'
            })
    else:
        return render(request, 'staff/login.html', {})


@login_required
def dashboard(request):
    if request.user.is_staff:
        # send_onboard_email(toemail='blablabla@gmail.com')
        today = datetime.now() + timedelta(hours=5, minutes=30)
        today_date = today.date()
        feedback_list = Feedback.objects.filter()
        nb_feedbacks = feedback_list.count()
        nb_bentities = BEntity.objects.count()
        nb_feedbacks_today = 0
        bentity_list = []
        customers = Feedback.objects.filter().values('customer').distinct()
        nb_customers = len(customers)
        for feedback in feedback_list:
            if feedback.timestamp.date() == today_date:
                nb_feedbacks_today += 1
        bentities = BEntity.objects.filter()
        for bentity in bentities:
            stats = {
                'greys': 0,
                'greens': 0,
                'customers': 0,
                'overall_rating': 0
            }
            try:
                stats = StatsBEntity.objects.get(b_entity=bentity)
            except StatsBEntity.DoesNotExist:
                pass
            stats_daily = []
            for i in range(0, 5):
                date = today_date - timedelta(days=i)
                try:
                    daily_stats = StatsBEntityDaily.objects.get(b_entity=bentity, date=date)
                    stat = {
                        'date': date,
                        'greys': daily_stats.greys,
                        'greens': daily_stats.greens,
                    }
                except StatsBEntityDaily.DoesNotExist:
                    stat = {
                        'date': date,
                        'greys': 0,
                        'greens': 0,
                    }
                stats_daily.append(stat)
            try:
                balance_account = BalanceAccountHolder.objects.get(b_entity=bentity).balance_account
                try:
                    asset_account = AssetAccount.objects.get(balance_account=balance_account)
                except BalanceAccount.DoesNotExist:
                    asset_account = None
            except BalanceAccountHolder.DoesNotExist:
                balance_account = None
                asset_account = None
            bentity_list.append({
                'bentity': bentity,
                'balance_account': balance_account,
                'asset_account': asset_account,
                'stats': stats,
                'stats_daily': stats_daily
            })
        return render(request, 'staff/dashboard.html', {
            'user': request.user,
            'stats': {
                'total':{
                    'nb_feedbacks': nb_feedbacks,
                    'nb_customers': nb_customers,
                    'nb_bentities': nb_bentities,
                },
                'today': {
                    'nb_feedbacks': nb_feedbacks_today,
                },
            },
            'bentity_list': bentity_list,
        })


@login_required
def dashboard_recharge(request):
    if request.user.is_staff:
        error = ""
        success = ""
        balance_account_holders_list = []
        balance_account_holders = BalanceAccountHolder.objects.filter()
        for balance_account_holder in balance_account_holders:
            if balance_account_holder.balance_account.status == "OPEN":
                balance_account_holders_list.append(balance_account_holder)
        if request.method == "POST":
            form = request.POST
            if form.get('b_entity') != 0 and form.get('b_entity') != '0':
                ba_holder = get_object_or_404(BalanceAccountHolder, b_entity=form.get('b_entity'))
                if do_recharge(ba_holder.balance_account, form.get('amount'), form.get('receipt_nb'), request.user):
                    success = 'Success! Recharge completed successfully.'
                else:
                    error = 'Error! Please try again.'
            else:
                error = 'Please select a valid Restaurant !'
        return render(request, 'staff/dashboard_recharge.html', {
            'user': request.user,
            'balance_account_holders': balance_account_holders_list,
            'error': error,
            'success': success,
        })


@login_required
def dashboard_market(request):
    if request.user.is_staff:
        products = Product.objects.filter()
        product_category = ProductCategory.objects.filter()
        return render(request, 'staff/dashboard_market.html', {
            'user': request.user,
            'products': products,
            'product_categories': product_category,
        })


@login_required
def dashboard_promosms(request):
    if request.user.is_staff:
        success = ''
        error = ''
        promosms_list = PromoSMS.objects.filter()
        b_entities = BEntity.objects.filter()
        if request.method == "POST":
            form = request.POST
            if form.get('id') > 0:
                form = request.POST
                post = PromoSMS.objects.get(pk=form.get('id'))
                active = False
                if form.get('status') == 'true':
                    active = True
                post.active = active
                post.save()
                return redirect('staff_dashboard_promosms')
            else:
                active = False
                if form.get('active'):
                    active = True
                if form.get('type'):
                    if form.get('b_entity') != 0 and form.get('b_entity') != '0':
                        t_type = "PERSONAL"
                        b_entity = get_object_or_404(BEntity, pk=form.get('b_entity'))
                        PromoSMS.objects.create(b_entity=b_entity, title=form.get('title'), content=form.get('content'),
                                                type=t_type, active=active, archive=False)
                        success = 'Success! Promo SMS template added successfully.'
                        error = ''
                    else:
                        success = ''
                        error = 'Please select a valid Restaurant!'
                else:
                    t_type = "COMMON"
                    PromoSMS.objects.create(title=form.get('title'), content=form.get('content'),
                                            type=t_type, active=active, archive=False)
                    success = 'Success! Promo SMS template added successfully.'
                    error = ''
        return render(request, 'staff/dashboard_promosms.html', {
            'user': request.user,
            'promosms_list': promosms_list,
            'b_entities': b_entities,
            'success': success,
            'error': error,
        })


@login_required
def dashboard_buy(request, pk):
    if request.user.is_staff:
        success = ''
        error = ''
        product = Product.objects.get(pk=pk)
        package_products = PackageProduct.objects.filter(package=product)
        bentity_list = []
        balance_account_holders = BalanceAccountHolder.objects.filter()
        for balance_account_holder in balance_account_holders:
            bentity_list.append([balance_account_holder.b_entity, balance_account_holder.balance_account.balance])
        if request.method == "POST":
            form = request.POST
            if form.get('b_entity') != 0 and form.get('b_entity') != '0':
                ba_holder = get_object_or_404(BalanceAccountHolder, b_entity=form.get('b_entity'))
                balance_account = ba_holder.balance_account
                quantity = float(form.get('quantity'))
                total_price = quantity * float(product.price)

                if (balance_account.balance+balance_account.credit_limit) > total_price:
                    product_list = []
                    product_list.append({'product': product, 'quantity': quantity})
                    order = do_order(balance_account, request.user, product_list)
                    if order:
                        success = 'Success! Product has been brought.'
                    else:
                        error = 'Oops! Please try again.'
                else:
                    error = 'Insufficient Balance !'
            else:
                error = 'Please select a valid Restaurant !'

        if product.unlimited_stock:
            product.stock = 'Unlimited'
        if product.unlimited_unit:
            product.unit = 'Unlimited'
        if product.unlimited_validity:
            product.validity = 'Unlimited'

        return render(request, 'staff/dashboard_buy.html', {
            'user': request.user,
            'product': product,
            'package_products': package_products,
            'bentity_list': bentity_list,
            'success': success,
            'error': error,
        })


@login_required
def dashboard_reports(request):
    if request.user.is_staff:
        bentity_list = BEntity.objects.filter()
        error = ''
        data = []
        now = datetime.now() + timedelta(hours=5, minutes=30)
        yesterday_date = now.date() - timedelta(days=1)

        if request.method == 'POST':
            form = request.POST
            if form.get('submit') == 'send_reports':
                bentity_pk_list = form.getlist("pk")
                now = datetime.now() + timedelta(hours=5, minutes=30)
                yesterday_date = now.date() - timedelta(days=1)
                if not ReportsSent.objects.filter(user=request.user, date=yesterday_date).exists():
                    # Send Daily Report SMS to B Entity
                    for pk in bentity_pk_list:
                        b_entity = BEntity.objects.get(pk=pk)
                        mobile_list = []

                        try:
                            stats = StatsBEntity.objects.get(b_entity=b_entity)
                        except StatsBEntity.DoesNotExist:
                            stats = StatsBEntity.objects.create(b_entity=b_entity)

                        try:
                            stats_daily = StatsBEntityDaily.objects.get(b_entity=b_entity, date=yesterday_date)
                        except StatsBEntityDaily.DoesNotExist:
                            stats_daily = StatsBEntityDaily.objects.create(b_entity=b_entity, date=yesterday_date)

                        message = urlquote('Dear Business Partner,\n' +
                                           b_entity.name + ' yesterday collected Total feedbacks ' +
                                           str(int(stats_daily.greys) + int(stats_daily.greens)) + ' Nos\n' +
                                           str(stats_daily.greens) + ' are Happy\n' +
                                           str(stats_daily.greys) + ' are Unhappy\n' +
                                           'Overall Rating is ' + str(round(stats.overall_rating, 1)) + ',\n' +
                                           'Thank You!')
                        mobile_list.append(str(b_entity.mobile))

                        if AlertList.objects.filter(b_entity=b_entity).exists:
                            nfa_list = AlertList.objects.filter(b_entity=b_entity, daily_reports_sms=True,
                                                                archive=False)
                            for dr_mobile in nfa_list:
                                mobile_list.append(str(dr_mobile.mobile))
                        send_message(mobile_list, message)
                    ReportsSent.objects.create(user=request.user, date=yesterday_date)
                else:
                    error = "Reports for yesterday already have been sent!"

        for b_entity in bentity_list:
            try:
                stats = StatsBEntity.objects.get(b_entity=b_entity)
            except StatsBEntity.DoesNotExist:
                stats = StatsBEntity.objects.create(b_entity=b_entity)

            try:
                stats_daily = StatsBEntityDaily.objects.get(b_entity=b_entity, date=yesterday_date)
            except StatsBEntityDaily.DoesNotExist:
                stats_daily = StatsBEntityDaily.objects.create(b_entity=b_entity, date=yesterday_date)

            data.append({'pk': b_entity.pk, 'name': b_entity.name, 'nb_feedbacks':
                        int(stats_daily.greys)+int(stats_daily.greens), 'nb_greens': int(stats_daily.greens),
                         'nb_greys': int(stats_daily.greys),
                         'overall_rating': float(round(stats.overall_rating))})

        return render(request, 'staff/dashboard_reports.html', {
            'bentity_list': data,
            'error': error,
        })


@login_required
def dashboard_account_activation(request):
    if request.user.is_staff:
        success = ''
        error = ''
        empty = ''
        users = ''
        if User.objects.filter(is_active=False).exists():
            users = User.objects.filter(is_active=False)
        else:
            empty = 'No Inactive users!'
        if request.method == 'POST':
            form = request.POST
            user = get_object_or_404(User, username=form.get('submit'))
            user.is_active = True
            user.save()
            success = 'User has been activated!'
        return render(request, 'staff/dashboard_account_activation.html', {
            'users': users,
            'success': success,
            'error': error,
            'empty': empty,
        })


@login_required
def dashboard_import(request):
    if request.user.is_staff:
        error = ''
        success = ''
        bentity_list = BEntity.objects.filter()
        if request.method == "POST":
            form = request.POST
            bentity = False
            if form.get('bentity') != -1 and form.get('bentity') != '-1':
                file = request.FILES['fileUpload']
                data = [row for row in csv.reader(file.read().splitlines())]
                i = 0
                for row in data:
                    if i == 0:
                        fields = row
                    else:
                        try:
                            if form.get('bentity') == '0':
                                bentity = BEntity.objects.get(name=row[1])
                            else:
                                bentity = BEntity.objects.get(name=form.get('bentity'))
                        except BEntity.DoesNotExist:
                            continue

                        if bentity:
                            if User.objects.filter(first_name__contains=row[2]).exists():
                                user = User.objects.filter(first_name__contains=row[2])[0]
                            else:
                                continue

                            try:
                                incharge = Incharge.objects.get(user=user, b_entity=bentity)
                            except Incharge.DoesNotExist:
                                continue

                            if Employee.objects.filter(first_name=row[4]).exists():
                                employee = Employee.objects.filter(first_name=row[4])[0]
                            else:
                                continue

                            mobile, created = Mobile.objects.get_or_create(number=row[7])

                            try:
                                customer = Customer.objects.get(mobile=mobile)
                            except Customer.DoesNotExist:
                                customer = Customer.objects.create(first_name=row[6], mobile=mobile)

                            if Feedback.objects.filter(b_entity=bentity, employee=employee, customer=customer,
                                                       comment__contains=row[15], incharge=incharge).exists():
                                feedback = Feedback.objects.filter(b_entity=bentity, employee=employee,
                                                                   customer=customer, comment__contains=row[15],
                                                                   incharge=incharge)[0]
                                feedback.timestamp = parse_datetime(row[16])
                                feedback.save()
                            else:
                                feedback = Feedback.objects.create(b_entity=bentity, employee=employee,
                                                                   customer=customer, comment=row[15],
                                                                   incharge=incharge, timestamp=parse_datetime(row[16]))

                                QS1.objects.create(feedback=feedback, rating=row[8])
                                QS2.objects.create(feedback=feedback, rating=row[9])
                                QS3.objects.create(feedback=feedback, rating=row[10])
                                QS4.objects.create(feedback=feedback, rating=row[11])
                                QD1.objects.create(feedback=feedback, rating=row[12])
                                QD2.objects.create(feedback=feedback, rating=row[13])
                    i += 1
                success = 'Success! Data Imported successfully.'
            else:
                error = 'Please select a valid Restaurant !'
        return render(request, 'staff/dashboard_import.html', {
            'bentity_list': bentity_list,
            'error': error,
            'success': success,
        })


@login_required
def dashboard_customers_b2c(request):
    if request.user.is_staff:
        error = ''
        success = ''
        b_entity = ''
        data = []
        bentity_list = BEntity.objects.filter()
        if request.method == "POST":
            form = request.POST
            if form.get('bentity') != -1 and form.get('bentity') != '-1':
                b_entity = get_object_or_404(BEntity,pk=form.get('bentity'))
                feedbacks = Feedback.objects.filter(b_entity=b_entity).values_list('customer', flat=True).distinct()
                customers = []
                for feedback in feedbacks:
                    customer = get_object_or_404(Customer, pk=feedback)
                    feebacks_by_customer = Feedback.objects.filter(customer=customer, b_entity=b_entity)\
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
            else:
                error = 'Please select a valid Restaurant !'
    return render(request, 'staff/dashboard_customers_b2c.html', {
        'b_entity': b_entity,
        'bentity_list': bentity_list,
        'customers': data,
        'error': error,
        'success': success,
    })


@login_required
def dashboard_customers_b2b(request):
    if request.user.is_staff:
        bentity_list = []
        bentities = BEntity.objects.filter()
        for bentity in bentities:
            try:
                incharge = Incharge.objects.get(b_entity=bentity)
                try:
                    user_profile = UserProfile.objects.get(user=incharge.user)
                except UserProfile.DoesNotExist:
                    user_profile = None
            except Incharge.DoesNotExist:
                incharge = None
                user_profile = None

            try:
                balance_account = BalanceAccountHolder.objects.get(b_entity=bentity).balance_account
                try:
                    asset_account = AssetAccount.objects.get(balance_account=balance_account)
                except AssetAccount.DoesNotExist:
                    asset_account = None
            except BalanceAccountHolder.DoesNotExist:
                balance_account = None
                asset_account = None

            bentity_list.append({
                'bentity': bentity,
                'incharge': incharge,
                'user_profile': user_profile,
                'balance_account': balance_account,
                'asset_account': asset_account,
            })
        return render(request, 'staff/dashboard_customers_b2b.html', {
            'bentity_list': bentity_list,
        })


@login_required
def dashboard_cache(request):
    if request.user.is_staff:
        if request.method == "POST":
            form = request.POST
            if form.get('submit') == 'all':
                # Truncate tables
                StatsBEntity.objects.all().delete()
                StatsBEntityDaily.objects.all().delete()
                StatsBEntityHourly.objects.all().delete()

                # Recreate cache
                feedbacks = Feedback.objects.filter()
                b_entities = BEntity.objects.filter()
                for b_entity in b_entities:
                    customers = Feedback.objects.filter(b_entity=b_entity).order_by().values_list('customer').distinct()
                    try:
                        stats = StatsBEntity.objects.get(b_entity=b_entity)
                        stats.customers = len(customers)
                        stats.save()
                    except StatsBEntity.DoesNotExist:
                        StatsBEntity.objects.create(b_entity=b_entity, customers=len(customers))

                for feedback in feedbacks:
                    timestamp = feedback.timestamp

                    try:
                        stats = StatsBEntity.objects.get(b_entity=feedback.b_entity)
                        nb_feedbacks_prev = stats.greys + stats.greens
                        if feedback.if_green():
                            stats.greens += 1
                        else:
                            stats.greys += 1
                        stats.overall_rating = ((stats.overall_rating * nb_feedbacks_prev) +
                                                feedback.get_overall_rating()) / (stats.greens + stats.greys)
                        stats.save()
                    except StatsBEntity.DoesNotExist:
                        if feedback.if_green():
                            greens = 1
                            greys = 0
                        else:
                            greens = 0
                            greys = 1
                        StatsBEntity.objects.create(b_entity=feedback.b_entity, greens=greens, greys=greys)

                    try:
                        stats = StatsBEntityDaily.objects.get(b_entity=feedback.b_entity, date=timestamp.date())
                        if feedback.if_green():
                            stats.greens += 1
                        else:
                            stats.greys += 1
                        stats.save()
                    except StatsBEntityDaily.DoesNotExist:
                        if feedback.if_green():
                            greens = 1
                            greys = 0
                        else:
                            greens = 0
                            greys = 1
                        StatsBEntityDaily.objects.create(b_entity=feedback.b_entity, greens=greens, greys=greys,
                                                         date=timestamp.date())

                    try:
                        stats = StatsBEntityHourly.objects.get(b_entity=feedback.b_entity, date=timestamp.date(),
                                                               hour=timestamp.hour)
                        if feedback.if_green():
                            stats.greens += 1
                        else:
                            stats.greys += 1
                        stats.save()
                    except StatsBEntityHourly.DoesNotExist:
                        if feedback.if_green():
                            greens = 1
                            greys = 0
                        else:
                            greens = 0
                            greys = 1
                        StatsBEntityHourly.objects.create(b_entity=feedback.b_entity, greens=greens, greys=greys,
                                                          date=timestamp.date(), hour=timestamp.hour)

    return render(request, 'staff/dashboard_cache.html', {})