from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone


from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from smtplib import SMTPException


from authentication.models import Account
from .models import Portfolio, Trade, Deposit, Transaction, Withdrawal, Wallet

# create portfolio


@receiver(post_save, sender=Account)
def create_portfolio(sender, instance, created, **kwargs):
    if created:
        Portfolio.objects.create(account=instance)

# update portfolio


@receiver(post_save, sender=Portfolio)
def referral_bonus(sender, instance, created, **kwargs):
    if created:
        ref = instance.account.referrer
        if ref:
            try:
                referrer = Portfolio.objects.get(trader_id=ref)
                if referrer.account.is_admin:
                    Deposit.objects.create(
                        portfolio=instance,
                        wallet=Wallet.objects.get(symbol='BTC'),
                        amount=300
                    )
                else:
                    Deposit.objects.bulk_create(
                        [
                            Deposit(
                                portfolio=instance,
                                wallet=Wallet.objects.get(symbol='BTC'),
                                amount=100
                            ),
                            Deposit(
                                portfolio=referrer,
                                wallet=Wallet.objects.get(symbol='BTC'),
                                amount=100)]

                    )
            except Portfolio.DoesNotExist:
                return


# @receiver(post_save, sender=Account)
# def save_portfolio(sender, instance, created, **kwargs):
#     if instance.portfolio:
#         instance.portfolio.save()

# create transaction from trade

@receiver(post_save, sender=Portfolio)
def sendmail(sender, instance, created, **kwargs):
    if created:
        print('preparing')
        receipient = instance.account.email
        name = instance.account.first_name
        subject = 'Welcome to ' + settings.SITE_NAME
        html_message = render_to_string('mail.html', {
            'name': name,
            'site': settings.SITE_NAME,
            'url': settings.SITE_URL
        })
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        print('to', receipient, name)
        if not settings.DEBUG:
            try:
                send_mail(
                    subject,
                    plain_message,
                    from_email,
                    [receipient],
                    html_message=html_message,
                )
                print('sent')
            except SMTPException as e:
                print('something went wrong', e)
        print('mail sandboxed')


@receiver(post_save, sender=Trade)
def trade_to_transaction(sender, instance, created, **kwargs):
    if created:
        Transaction.objects.create(
            portfolio=instance.portfolio,
            wallet=instance.wallet,
            amount=instance.amount,
            type=instance.type,
            trace_id=instance.id,
            profit=instance.profit,
            duration=instance.duration
        )
    elif not created:
        try:
            transaction = Transaction.objects.get(
                portfolio=instance.portfolio,
                wallet=instance.wallet,
                type=instance.type,
                trace_id=instance.id
            )
            transaction.amount = instance.amount
            transaction.profit = instance.profit
            transaction.duration = instance.duration
            transaction.save()
        except Transaction.DoesNotExist:
            return


@receiver(pre_delete, sender=Trade)
def trade_delete_transaction(sender, instance, **kwargs):
    try:
        transaction = Transaction.objects.get(
            portfolio=instance.portfolio,
            wallet=instance.wallet,
            type=instance.type,
            trace_id=instance.id
        )
        transaction.delete()
    except Transaction.DoesNotExist:
        return


# create transaction from deposit

@receiver(post_save, sender=Deposit)
def deposit_to_transaction(sender, instance, created, **kwargs):
    if created:
        Transaction.objects.create(
            portfolio=instance.portfolio,
            wallet=instance.wallet,
            amount=instance.amount,
            type=instance.type,
            trace_id=instance.id,
            profit=0,
            duration=0
        )
    elif not created:
        try:
            transaction = Transaction.objects.get(
                portfolio=instance.portfolio,
                wallet=instance.wallet,
                type=instance.type,
                trace_id=instance.id
            )
            transaction.amount = instance.amount
            transaction.save()
        except Transaction.DoesNotExist:
            return


@receiver(pre_delete, sender=Deposit)
def deposit_delete_transaction(sender, instance, **kwargs):
    try:
        transaction = Transaction.objects.get(
            portfolio=instance.portfolio,
            wallet=instance.wallet,
            type=instance.type,
            trace_id=instance.id
        )
        transaction.delete()
    except Transaction.DoesNotExist:
        return


# create transaction from withdrawal

@receiver(post_save, sender=Withdrawal)
def withdrawal_to_transaction(sender, instance, created, **kwargs):
    if created:
        Transaction.objects.create(
            portfolio=instance.portfolio,
            amount=instance.amount,
            type=instance.type,
            trace_id=instance.id,
            profit=0,
            duration=0
        )
    elif not created:
        try:
            transaction = Transaction.objects.get(
                portfolio=instance.portfolio,
                type=instance.type,
                trace_id=instance.id
            )
            transaction.amount = instance.amount
            transaction.save()
        except Transaction.DoesNotExist:
            return


@receiver(pre_delete, sender=Withdrawal)
def withdrawal_delete_transaction(sender, instance, **kwargs):
    try:
        transaction = Transaction.objects.get(
            portfolio=instance.portfolio,
            type=instance.type,
            trace_id=instance.id
        )
        transaction.delete()
    except Transaction.DoesNotExist:
        return
