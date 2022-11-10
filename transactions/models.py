from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import F


class Account(models.Model):
    balance = models.FloatField(validators=[MinValueValidator(0)])
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    transactions = models.ManyToManyField('self', through='Transaction')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Cчет'
        verbose_name_plural = 'Cчета'


class Transaction(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(validators=[MinValueValidator(0)])
    from_accounts = models.ManyToManyField(Account, related_name='outcomes')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='incomes')
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    @staticmethod
    def create_transaction(to_account, from_accounts, amount):
        accounts_count = from_accounts.count()
        # for account in from_accounts:
        #     if account.balance < amount/accounts_count:
        #         form.add_error('from_accounts', f'Account {account.id} does not have sufficient funds.')
        #         break
        # print(from_accounts.filter(balance__gte=amount/accounts_count).query)
        sufficient_accounts = from_accounts.filter(balance__gte=amount/accounts_count)
        if sufficient_accounts.count() < accounts_count:
            insufficient_accounts = set(from_accounts.values_list('id', flat=True)) - set(sufficient_accounts.values_list('id', flat=True))
            raise ValueError(f'Accounts {",".join(map(str,insufficient_accounts))} do not have sufficient funds.')
        from_accounts.update(balance=F('balance') - amount/accounts_count)
        to_account.balance += amount
        to_account.save()
        # for account in from_accounts:
        #     Transaction.objects.create(from_account=account, to_account=to_account, amount=amount/accounts_count)
        # transaction_list = []
        # for account in from_accounts:
        #     transaction_list.append(Transaction(from_account=account, to_account=to_account, amount=amount/accounts_count))
        # Transaction.objects.bulk_create(transaction_list)
        transaction = Transaction.objects.create(to_account=to_account, amount=amount)
        transaction.from_accounts.add(*from_accounts)
        return transaction


    def cancel(self):
        self.to_account.balance -= self.amount
        self.to_account.save()
        self.from_accounts.update(balance=F('balance') - self.amount/self.from_accounts.count())
        self.is_cancelled = True
        self.save()







