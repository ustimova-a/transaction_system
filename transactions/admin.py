from django.contrib import admin
from .models import Account, Transaction


class TransactionIncomeInline(admin.TabularInline):
    model = Account.transactions.through
    fk_name = 'to_account'
    verbose_name_plural = 'Поступления'
    extra = 0


class TransactionOutcomeInline(admin.TabularInline):
    model = Transaction.from_accounts.through
    # fk_name = 'from_accounts'
    verbose_name_plural = 'Расходы'
    extra = 0


class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'balance', 'user', 'created')
    inlines = (TransactionIncomeInline, TransactionOutcomeInline)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'from_accounts_list', 'to_account', 'is_cancelled')
    def from_accounts_list(self, transaction):
        return ', '.join(transaction.from_accounts.values_list('id', flat=True))
    

admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
