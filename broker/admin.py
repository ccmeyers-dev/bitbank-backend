from django.contrib import admin
from .models import Portfolio, Wallet, Deposit, Trade, Transaction, Withdrawal, Billing
# Register your models here.


class BillingAdmin(admin.ModelAdmin):
    list_display = ('withdrawal', 'title', 'amount')
    list_filter = ('withdrawal', 'title',)
    search_fields = ('withdrawal', 'title')


admin.site.register(Billing, BillingAdmin)


class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('account', 'full_name', 'trader_id')
    search_fields = ('account', 'trader_id')


admin.site.register(Portfolio, PortfolioAdmin)


class WalletAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'symbol', 'address')


admin.site.register(Wallet, WalletAdmin)


class DepositAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'amount', 'wallet')
    list_filter = ('wallet', 'portfolio',)
    search_fields = ('portfolio', 'wallet')


admin.site.register(Deposit, DepositAdmin)


class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'amount', 'wallet')
    list_filter = ('portfolio', 'amount',)
    search_fields = ('portfolio', 'amount')


admin.site.register(Withdrawal, WithdrawalAdmin)


class TradeAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'amount', 'wallet',
                    'profit', 'duration', 'type', 'withdrawal_date')
    list_filter = ('wallet', 'portfolio',)
    search_fields = ('portfolio', 'wallet',)


admin.site.register(Trade, TradeAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'amount', 'type',
                    'profit', 'duration', 'withdrawal_date')


admin.site.register(Transaction, TransactionAdmin)
