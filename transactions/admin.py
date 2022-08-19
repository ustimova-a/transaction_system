from django.contrib import admin
from .models import Account, Transaction


class TransactionIncomeInline(admin.TabularInline):
    model = Account.transactions.through
    fk_name = 'to_account'
    verbose_name_plural = 'Поступления'
    extra = 0


class TransactionOutcomeInline(admin.TabularInline):
    model = Account.transactions.through
    fk_name = 'from_account'
    verbose_name_plural = 'Расходы'
    extra = 0


class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'balance', 'user', 'created')
    inlines = (TransactionIncomeInline, TransactionOutcomeInline)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'date_time', 'from_account', 'to_account')


admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
