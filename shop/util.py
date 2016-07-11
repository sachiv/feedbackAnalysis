from django.shortcuts import get_object_or_404
from shop.models import *
from feedbackanalysis.util import urlquote
from sms.util import send_message
from b2b.models import BEntity
from registration.models import UserProfile
from datetime import datetime, timedelta


def update_assets(assetsaccount, product, add, quantity, validity=-1):
    if validity == -1:
        validity = product.validity
    asset_account = get_object_or_404(AssetAccount, pk=assetsaccount.pk)
    if product.category == get_object_or_404(ProductCategory, name="PROMO SMS"):
        if add:
            asset_account.sms_promo += (int(quantity) * int(product.unit))
            asset_account.sms_promo_validity = datetime.now() + timedelta(hours=5, minutes=30) \
                                               + timedelta(days=int(validity))
        else:
            asset_account.sms_promo -= int(quantity)
    elif product.category == get_object_or_404(ProductCategory, name="THANK YOU SMS"):
        asset_account.sms_thankyou_validity = datetime.now() + timedelta(hours=5, minutes=30) \
                                           + timedelta(days=int(validity))
    elif product.category == get_object_or_404(ProductCategory, name="NFA SMS"):
        asset_account.sms_nfa_validity = datetime.now() + timedelta(hours=5, minutes=30) \
                                              + timedelta(days=int(validity))
    asset_account.save()
    return True


def do_transaction(amount, trans_type, status):
    transaction = Transaction.objects.create(amount=amount, type=trans_type, status=status)
    if transaction:
        return transaction
    else:
        return False


def do_recharge(balance_account, amount, receipt_nb, staff, payment_mode='CASH'):
    transaction = do_transaction(amount, "RECHARGE", "STARTED")
    if transaction:
        if balance_account.status == 'OPEN':
            if balance_account:
                Recharge.objects.create(transaction=transaction, amount=amount, receipt_nb=receipt_nb,
                                        destination=balance_account, staff=staff, payment_mode=payment_mode)
                balance_account.balance += float(amount)
                balance_account.save()
                transaction.status = "SUCCESS"
                transaction.save()

                # Send Recharge Message
                mobiles_list = list()
                message = urlquote("Dear Business Partner, Your account is recharged with " +
                                   str(amount)+" your prepaid balance is "+str(balance_account.balance))
                if BalanceAccountHolder.objects.filter(balance_account=balance_account).exists():
                    balance_account_holder = BalanceAccountHolder.objects.get(balance_account=balance_account)
                    mobiles_list.append(str(balance_account_holder.b_entity.mobile))
                    send_message(mobiles_list, message)
            else:
                transaction.status = "FAILED"
                transaction.save()
                return False
    else:
        transaction.status = "FAILED"
        transaction.save()
        return False
    return True


def do_order(balance_account, user, products_list, amount=-1):
    print products_list
    if balance_account.status == "OPEN":
        total_amount = 0
        if amount == -1:
            for product in products_list:
                total_amount += product['product'].price * float(product['quantity'])
        else:
            total_amount = amount
        transaction = do_transaction(total_amount, "ORDER", "STARTED")
        if transaction:
            order = Order.objects.create(transaction=transaction, amount=total_amount, account=balance_account,
                                         ordered_by=user, payed=total_amount)
            if order:
                check = 0
                for product in products_list:
                    order_product = OrderProduct.objects.create(order=order, product=product['product'],
                                                                quantity=product['quantity'])
                    if order_product:
                        # Update Stock
                        product['product'].stock -= product['quantity']
                        product['product'].save()
                        # Update Assets
                        assetsaccount = AssetAccount.objects.get(balance_account=balance_account)
                        if not update_assets(assetsaccount, product['product'], True, product['quantity']):
                            check = 1
                        # Update individual package assets
                        if PackageProduct.objects.filter(package=product['product']).exists():
                            for package_product in PackageProduct.objects.filter(package=product['product']):
                                if not update_assets(assetsaccount, package_product.product, True,
                                                     package_product.quantity, product['product'].validity):
                                    check = 1
                    # Update Balance
                    balance_account.balance -= float(product['product'].price)
                    balance_account.save()
                if check == 0:
                    transaction.status = "SUCCESS"
                    transaction.save()
                    return True
        transaction.status = "FAILED"
        transaction.save()
    return False