from email import message
from django.shortcuts import render
from django.db.models import F
from django.contrib.auth.forms import UserCreationForm

from .models import Account, Transaction
from .forms import TransactionForm, TransactionFilterForm
from .filters import TransactionFilter, AccountFilter

def transaction(request):
    message = ''
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            from_accounts = form.cleaned_data.get('from_accounts')
            # print(from_accounts.query)
            to_account = form.cleaned_data.get('to_account')
            amount = form.cleaned_data.get('amount')
            accounts_count = from_accounts.count()
            # for account in from_accounts:
            #     if account.balance < amount/accounts_count:
            #         form.add_error('from_accounts', f'Account {account.id} does not have sufficient funds.')
            #         break
            # print(from_accounts.filter(balance__gte=amount/accounts_count).query)
            if from_accounts.filter(balance__gte=amount/accounts_count).count() < accounts_count:
                form.add_error('from_accounts', f'Account {Account.id} does not have sufficient funds.')
            else:
                # for account in from_accounts:
                #     account.balance -= amount/accounts_count
                #     account.save()
                from_accounts.update(balance=F('balance') - amount/accounts_count)
                to_account.balance += amount
                to_account.save()
                # for account in from_accounts:
                #     Transaction.objects.create(from_account=account, to_account=to_account, amount=amount/accounts_count)
                transaction_list = []
                for account in from_accounts:
                    transaction_list.append(Transaction(from_account=account, to_account=to_account, amount=amount/accounts_count))
                Transaction.objects.bulk_create(transaction_list)
                message = 'Successful transaction.'
    else:
        form = TransactionForm(request.user)
    return render(request, 'transaction.html', {'filter_form': form, 'message': message})


def filter_transactions(request):
    filter = TransactionFilter(request.GET, queryset=Transaction.objects.all(), request=request)
    return render(request, 'filter_transactions.html', {'filter': filter})


def account(request):
    filter = AccountFilter(request.GET, queryset=Account.objects.all())
    return render(request, 'account.html', {'filter': filter})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration.html', {'form': form})
