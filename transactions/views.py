from email import message
from django.shortcuts import render
from django.db.models import F

from .models import Account
from .forms import TransactionForm

def transaction(request):
    message = ''
    if request.method == 'POST':
        form = TransactionForm(request.POST)
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
                message = 'Successful transaction.'
    else:
        form = TransactionForm()
    return render(request, 'transaction.html', {'filter_form': form, 'message': message})
