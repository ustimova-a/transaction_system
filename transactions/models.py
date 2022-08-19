from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    balance = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    transactions = models.ManyToManyField('self', through='Transaction')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Cчет'
        verbose_name_plural = 'Cчета'


class Transaction(models.Model):
    amount = models.FloatField()
    date_time = models.DateTimeField(auto_now_add=True)
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='outcomes')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='incomes')

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'




